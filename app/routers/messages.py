from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.notification import Notification
from app.models.user import User
from app.models.workers import Worker
from app.schemas.message import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)

router = APIRouter(prefix="/messages", tags=["Messages"])


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _conversation_query_for_user(db: Session, user_email: str):
    return db.query(Conversation).filter(
        or_(
            Conversation.participant_one_email == user_email,
            Conversation.participant_two_email == user_email,
        )
    )


def _other_participant(conversation: Conversation, user_email: str) -> str:
    if conversation.participant_one_email == user_email:
        return conversation.participant_two_email
    return conversation.participant_one_email


def _resolve_display_name(db: Session, email: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user.display_name
    return email.split("@")[0]


def _resolve_worker_name(db: Session, worker_id: int | None) -> str | None:
    if worker_id is None:
        return None
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        return None
    return worker.name


def _build_conversation_response(
    db: Session, conversation: Conversation, user_email: str
) -> ConversationResponse:
    participant_email = _other_participant(conversation, user_email)
    unread_count = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id,
            Message.recipient_email == user_email,
            Message.is_read == False,
        )
        .count()
    )
    
    # Use eager loaded worker if available to avoid N+1 query
    worker_name = None
    if conversation.worker:
        worker_name = conversation.worker.name
    elif conversation.worker_id:
        worker_name = _resolve_worker_name(db, conversation.worker_id)

    return ConversationResponse(
        id=conversation.id,
        participant_email=participant_email,
        participant_name=_resolve_display_name(db, participant_email),
        worker_id=conversation.worker_id,
        worker_name=worker_name,
        last_message=conversation.last_message,
        last_message_at=conversation.last_message_at,
        unread_count=unread_count,
    )


def _get_conversation_or_404(db: Session, conversation_id: int) -> Conversation:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def _assert_participant(conversation: Conversation, user_email: str) -> None:
    if user_email not in {
        conversation.participant_one_email,
        conversation.participant_two_email,
    }:
        raise HTTPException(status_code=403, detail="Access denied for conversation")


@router.get("/conversations", response_model=list[ConversationResponse])
def get_conversations(user_email: str = Query(...), db: Session = Depends(get_db)):
    user_email = _normalize_email(user_email)
    conversations = (
        _conversation_query_for_user(db, user_email)
        .options(joinedload(Conversation.worker))
        .order_by(Conversation.last_message_at.desc(), Conversation.id.desc())
        .all()
    )
    return [_build_conversation_response(db, conversation, user_email) for conversation in conversations]


@router.post("/conversations", response_model=ConversationResponse)
def create_or_get_conversation(
    payload: ConversationCreate, db: Session = Depends(get_db)
):
    sender_email = _normalize_email(payload.sender_email)
    recipient_email = _normalize_email(payload.recipient_email)

    if payload.worker_id is not None:
        worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        recipient_email = _normalize_email(worker.user_email)

    if sender_email == recipient_email:
        raise HTTPException(
            status_code=400,
            detail="You cannot message your own worker profile",
        )

    participants = sorted([sender_email, recipient_email])
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.participant_one_email == participants[0],
            Conversation.participant_two_email == participants[1],
            Conversation.worker_id == payload.worker_id,
        )
        .first()
    )

    if conversation is None:
        conversation = Conversation(
            participant_one_email=participants[0],
            participant_two_email=participants[1],
            worker_id=payload.worker_id,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    if payload.initial_message:
        send_message_to_conversation(
            conversation.id,
            MessageCreate(sender_email=sender_email, content=payload.initial_message),
            db,
            skip_commit=False,
        )
        conversation = _get_conversation_or_404(db, conversation.id)

    return _build_conversation_response(db, conversation, sender_email)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    conversation_id: int,
    user_email: str = Query(...),
    db: Session = Depends(get_db),
):
    user_email = _normalize_email(user_email)
    conversation = _get_conversation_or_404(db, conversation_id)
    _assert_participant(conversation, user_email)

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )
    participant_email = _other_participant(conversation, user_email)

    return ConversationDetailResponse(
        id=conversation.id,
        participant_email=participant_email,
        participant_name=_resolve_display_name(db, participant_email),
        worker_id=conversation.worker_id,
        worker_name=_resolve_worker_name(db, conversation.worker_id),
        messages=[MessageResponse.model_validate(message) for message in messages],
    )


@router.post("/conversations/{conversation_id}", response_model=MessageResponse)
def send_message_to_conversation(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    skip_commit: bool = False,
):
    sender_email = _normalize_email(payload.sender_email)
    conversation = _get_conversation_or_404(db, conversation_id)
    _assert_participant(conversation, sender_email)

    recipient_email = _other_participant(conversation, sender_email)
    message = Message(
        conversation_id=conversation.id,
        sender_email=sender_email,
        recipient_email=recipient_email,
        content=payload.content,
        is_read=False,
    )
    db.add(message)

    conversation.last_message = payload.content
    db.flush()
    db.refresh(message)
    conversation.last_message_at = message.created_at

    notification = Notification(
        user_email=recipient_email,
        title="New message",
        message=f"{_resolve_display_name(db, sender_email)} sent you a message",
        type="message",
        reference_id=conversation.id,
    )
    db.add(notification)

    if not skip_commit:
        db.commit()
        db.refresh(message)

    return MessageResponse.model_validate(message)


@router.put("/conversations/{conversation_id}/read")
def mark_conversation_as_read(
    conversation_id: int,
    user_email: str = Query(...),
    db: Session = Depends(get_db),
):
    user_email = _normalize_email(user_email)
    conversation = _get_conversation_or_404(db, conversation_id)
    _assert_participant(conversation, user_email)

    unread_messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.recipient_email == user_email,
            Message.is_read == False,
        )
        .all()
    )
    for message in unread_messages:
        message.is_read = True

    db.commit()
    return {"message": "Conversation marked as read"}


@router.get("/unread-count")
def get_unread_message_count(user_email: str = Query(...), db: Session = Depends(get_db)):
    user_email = _normalize_email(user_email)
    unread_count = (
        db.query(Message)
        .filter(Message.recipient_email == user_email, Message.is_read == False)
        .count()
    )
    return {"unread_count": unread_count}
