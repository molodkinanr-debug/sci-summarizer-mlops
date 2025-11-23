from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List
import re

@dataclass
class User:
    """
    Класс для представления пользователя в системе.
    
    Attributes:
        id (int): Уникальный идентификатор пользователя
        email (str): Email пользователя
        password (str): Пароль пользователя
        events (List[Event]): Список событий пользователя
    """
    id: int
    email: str
    password: str
    events: List['Event'] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_email()
        self._validate_password()

    def _validate_email(self) -> None:
        """Проверяет корректность email."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(self.email):
            raise ValueError("Invalid email format")

    def _validate_password(self) -> None:
        """Проверяет минимальную длину пароля."""
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

    def add_event(self, event: 'Event') -> None:
        """Добавляет событие в список событий пользователя."""
        self.events.append(event)

@dataclass
class Event:
    """
    Класс для представления события.
    
    Attributes:
        id (int): Уникальный идентификатор события
        title (str): Название события
        image (str): Путь к изображению события
        description (str): Описание события
        creator (User): Создатель события
    """
    id: int
    title: str
    image: str
    description: str
    creator: User

    def __post_init__(self) -> None:
        self._validate_title()
        self._validate_description()

    def _validate_title(self) -> None:
        """Проверяет длину названия события."""
        if not 1 <= len(self.title) <= 100:
            raise ValueError("Title must be between 1 and 100 characters")

    def _validate_description(self) -> None:
        """Проверяет длину описания события."""
        if len(self.description) > 500:
            raise ValueError("Description must not exceed 500 characters")



class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    ADMIN_DEPOSIT = "admin_deposit"

class RequestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    INSUFFICIENT_FUNDS = "insufficient_funds"

class BaseEntity(ABC):
    def __init__(self, id: UUID):
        self._id = id
        self._created_at = datetime.now()
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

class User(BaseEntity):
    def __init__(self, email: str, password_hash: str, name: str, 
                 role: User = User.USER, balance: float = 0.0):
        super().__init__(uuid4())
        self._email = email
        self._password_hash = password_hash
        self._name = name
        self._role = role
        self._balance = balance
        self._is_active = True
    
    # Геттеры и сеттеры с инкапсуляцией
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError("Invalid email format")
        self._email = value
    
    @property
    def balance(self) -> float:
        return self._balance
    
    def has_sufficient_balance(self, amount: float) -> bool:
        return self._balance >= amount
    
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
    
    def withdraw(self, amount: float) -> bool:
        if not self.has_sufficient_balance(amount):
            return False
        self._balance -= amount
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "email": self._email,
            "name": self._name,
            "role": self._role.value,
            "balance": self._balance,
            "is_active": self._is_active,
            "created_at": self._created_at.isoformat()
        }
    
class MLModel(ABC):
    def __init__(self, name: str, version: str, cost_per_request: float):
        self._name = name
        self._version = version
        self._cost_per_request = cost_per_request
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def cost_per_request(self) -> float:
        return self._cost_per_request
    
    @abstractmethod
    def preprocess(self, input_data: Any) -> Any:
        pass
    
    @abstractmethod
    def predict(self, processed_data: Any) -> Any:
        pass
    
    @abstractmethod
    def postprocess(self, prediction: Any) -> Any:
        pass
    
    # Полиморфизм: единый интерфейс для разных моделей
    def process(self, input_data: Any) -> Any:
        processed_data = self.preprocess(input_data)
        prediction = self.predict(processed_data)
        return self.postprocess(prediction)

class TextSummarizationModel(MLModel):
    def __init__(self, name: str, version: str, cost_per_request: float,
                 max_input_length: int):
        super().__init__(name, version, cost_per_request)
        self._max_input_length = max_input_length
    
    def preprocess(self, text: str) -> Dict[str, Any]:
        return {
            "cleaned_text": text.strip(),
            "length": len(text),
            "tokens": text.split()[:self._max_input_length]
        }
    
    def predict(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        text = processed_data["cleaned_text"]
        sentences = text.split('.')
        summary = '. '.join(sentences[:2]) + '.' if len(sentences) > 2 else text
        
        return {
            "original_length": len(text),
            "summary_length": len(summary),
            "summary_text": summary
        }
    
    def postprocess(self, prediction: Dict[str, Any]) -> str:
        return prediction["summary_text"]
    
class PDFFile(BaseEntity):
    def __init__(self, original_filename: str, file_path: str, file_size: int):
        super().__init__(uuid4())
        self._original_filename = original_filename
        self._file_path = file_path
        self._file_size = file_size
        self._extracted_text: Optional[str] = None
    
    @property
    def original_filename(self) -> str:
        return self._original_filename
    
    def set_extracted_text(self, text: str) -> None:
        self._extracted_text = text
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "original_filename": self._original_filename,
            "file_size": self._file_size,
            "has_text": self._extracted_text is not None,
            "created_at": self._created_at.isoformat()
        }

class Transaction(BaseEntity):
    def __init__(self, user_id: UUID, amount: float, 
                 transaction_type: TransactionType, description: str = ""):
        super().__init__(uuid4())
        self._user_id = user_id
        self._amount = amount
        self._transaction_type = transaction_type
        self._description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "user_id": str(self._user_id),
            "amount": self._amount,
            "transaction_type": self._transaction_type.value,
            "description": self._description,
            "created_at": self._created_at.isoformat()
        }
    
class PredictionRequest(BaseEntity):
    def __init__(self, user_id: UUID, pdf_file: PDFFile, model: MLModel):
        super().__init__(uuid4())
        self._user_id = user_id
        self._pdf_file = pdf_file  # Композиция
        self._model = model
        self._status = RequestStatus.PENDING
        self._cost = model.cost_per_request
        self._result: Optional[str] = None
    
    def process_request(self, user: User) -> bool:
        if not user.has_sufficient_balance(self._cost):
            self._status = RequestStatus.INSUFFICIENT_FUNDS
            return False
        
        if user.withdraw(self._cost):
            self._status = RequestStatus.PROCESSING
            # Здесь была бы реальная обработка PDF и текста
            if self._pdf_file._extracted_text:
                self._result = self._model.process(self._pdf_file._extracted_text)
                self._status = RequestStatus.SUCCESS
                return True
        
        self._status = RequestStatus.ERROR
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "user_id": str(self._user_id),
            "pdf_file": self._pdf_file.to_dict(),
            "model_name": self._model.name,
            "status": self._status.value,
            "cost": self._cost,
            "result": self._result,
            "created_at": self._created_at.isoformat()
        }
    
def main() -> None:
    try:
        user = User(
            id=1,
            email="test@mail.ru",
            password="secure_password123"
        )
        
        event = Event(
            id=1,
            title="First Event",
            image="image.jpg",
            description="Event description",
            creator=user
        )
        
        user.add_event(event)
        print(f"Created user: {user}")
        print(f"Number of user events: {len(user.events)}")
        
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
