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
    PAYMENT = "payment"
    REFUND = "refund"

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
                 role: UserRole = UserRole.USER):
        super().__init__(uuid4())
        self._email = email
        self._password_hash = password_hash
        self._name = name
        self._role = role
        self._is_active = True
        self._prediction_history: List['PredictionRequest'] = []
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError("Invalid email format")
        self._email = value
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def add_to_prediction_history(self, prediction_request: 'PredictionRequest') -> None:
        self._prediction_history.append(prediction_request)
    
    def get_prediction_history(self) -> List['PredictionRequest']:
        return self._prediction_history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "email": self._email,
            "name": self._name,
            "role": self._role.value,
            "is_active": self._is_active,
            "created_at": self._created_at.isoformat(),
            "prediction_count": len(self._prediction_history)
        }

class AccountManager(BaseEntity):
    """Управление балансами пользователей"""
    
    def __init__(self):
        super().__init__(uuid4())
        self._user_balances: Dict[UUID, float] = {}
        self._transaction_history: List['Transaction'] = []
    
    def create_account(self, user_id: UUID, initial_balance: float = 0.0) -> None:
        if user_id in self._user_balances:
            raise ValueError(f"Account for user {user_id} already exists")
        self._user_balances[user_id] = initial_balance
    
    def get_balance(self, user_id: UUID) -> float:
        return self._user_balances.get(user_id, 0.0)
    
    def has_sufficient_balance(self, user_id: UUID, amount: float) -> bool:
        return self.get_balance(user_id) >= amount
    
    def deposit(self, user_id: UUID, amount: float, description: str = "") -> bool:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        if user_id not in self._user_balances:
            self.create_account(user_id, 0.0)
        
        self._user_balances[user_id] += amount
        transaction = Transaction(user_id, amount, TransactionType.DEPOSIT, description)
        self._transaction_history.append(transaction)
        return True
    
    def withdraw(self, user_id: UUID, amount: float, description: str = "") -> bool:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if not self.has_sufficient_balance(user_id, amount):
            return False
        
        self._user_balances[user_id] -= amount
        transaction = Transaction(user_id, amount, TransactionType.WITHDRAWAL, description)
        self._transaction_history.append(transaction)
        return True
    
    def get_transaction_history(self, user_id: Optional[UUID] = None) -> List['Transaction']:
        if user_id:
            return [t for t in self._transaction_history if t.user_id == user_id]
        return self._transaction_history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "total_users": len(self._user_balances),
            "total_balance": sum(self._user_balances.values()),
            "total_transactions": len(self._transaction_history),
            "created_at": self._created_at.isoformat()
        }

class MLModel(ABC):
    def __init__(self, name: str, version: str, cost_per_request: float):
        self._name = name
        self._version = version
        self._cost_per_request = cost_per_request
        self._is_active = True
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def cost_per_request(self) -> float:
        return self._cost_per_request
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def activate(self) -> None:
        self._is_active = True
    
    def deactivate(self) -> None:
        self._is_active = False
    
    @abstractmethod
    def preprocess(self, input_data: Any) -> Any:
        pass
    
    @abstractmethod
    def predict(self, processed_data: Any) -> Any:
        pass
    
    @abstractmethod
    def postprocess(self, prediction: Any) -> Any:
        pass
    
    def process(self, input_data: Any) -> Any:
        if not self._is_active:
            raise RuntimeError("Model is not active")
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
    
    @property
    def file_path(self) -> str:
        return self._file_path
    
    @property
    def file_size(self) -> int:
        return self._file_size
    
    @property
    def extracted_text(self) -> Optional[str]:
        return self._extracted_text
    
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
    
    @property
    def user_id(self) -> UUID:
        return self._user_id
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def transaction_type(self) -> TransactionType:
        return self._transaction_type
    
    @property
    def description(self) -> str:
        return self._description
    
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
        self._pdf_file = pdf_file
        self._model = model
        self._status = RequestStatus.PENDING
        self._cost = model.cost_per_request
        self._result: Optional[str] = None
        self._processed_at: Optional[datetime] = None
    
    @property
    def user_id(self) -> UUID:
        return self._user_id
    
    @property
    def status(self) -> RequestStatus:
        return self._status
    
    @property
    def cost(self) -> float:
        return self._cost
    
    @property
    def result(self) -> Optional[str]:
        return self._result
    
    @property
    def processed_at(self) -> Optional[datetime]:
        return self._processed_at
    
    def process_request(self, account_manager: AccountManager) -> bool:
        if not account_manager.has_sufficient_balance(self._user_id, self._cost):
            self._status = RequestStatus.INSUFFICIENT_FUNDS
            return False
        
        if account_manager.withdraw(self._user_id, self._cost, f"Payment for {self._model.name}"):
            self._status = RequestStatus.PROCESSING
            
            try:
                if self._pdf_file.extracted_text:
                    self._result = self._model.process(self._pdf_file.extracted_text)
                    self._status = RequestStatus.SUCCESS
                    self._processed_at = datetime.now()
                    return True
                else:
                    self._status = RequestStatus.ERROR
                    # Возвращаем деньги при ошибке
                    account_manager.deposit(self._user_id, self._cost, "Refund for failed processing")
                    return False
            except Exception as e:
                self._status = RequestStatus.ERROR
                account_manager.deposit(self._user_id, self._cost, f"Refund for processing error: {str(e)}")
                return False
        
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
            "processed_at": self._processed_at.isoformat() if self._processed_at else None,
            "created_at": self._created_at.isoformat()
        }

class PredictionHistory(BaseEntity):
    """История предсказаний для пользователя"""
    
    def __init__(self, user_id: UUID):
        super().__init__(uuid4())
        self._user_id = user_id
        self._predictions: List[PredictionRequest] = []
    
    def add_prediction(self, prediction: PredictionRequest) -> None:
        self._predictions.append(prediction)
    
    def get_predictions(self, limit: Optional[int] = None) -> List[PredictionRequest]:
        if limit:
            return self._predictions[-limit:]
        return self._predictions.copy()
    
    def get_successful_predictions(self) -> List[PredictionRequest]:
        return [p for p in self._predictions if p.status == RequestStatus.SUCCESS]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self._id),
            "user_id": str(self._user_id),
            "total_predictions": len(self._predictions),
            "successful_predictions": len(self.get_successful_predictions()),
            "created_at": self._created_at.isoformat()
        }

def main() -> None:
    # Демонстрация работы обновленной модели
    try:
        # Создаем менеджер аккаунтов
        account_manager = AccountManager()
        
        # Создаем пользователя
        user = User(
            email="user@example.com",
            password_hash="hashed_password_123",
            name="John Doe"
        )
        
        # Создаем аккаунт для пользователя с начальным балансом
        account_manager.create_account(user.id, 100.0)
        
        # Создаем модель для суммаризации
        summarization_model = TextSummarizationModel(
            name="text-summarizer",
            version="1.0",
            cost_per_request=10.0,
            max_input_length=1000
        )
        
        # Создаем PDF файл
        pdf_file = PDFFile(
            original_filename="research_paper.pdf",
            file_path="/uploads/research_paper.pdf",
            file_size=1024000
        )
        pdf_file.set_extracted_text("This is a long research paper text that needs to be summarized...")
        
        # Создаем запрос на предсказание
        prediction_request = PredictionRequest(user.id, pdf_file, summarization_model)
        
        # Обрабатываем запрос
        if prediction_request.process_request(account_manager):
            print("Prediction processed successfully!")
            print(f"Result: {prediction_request.result}")
        else:
            print(f"Prediction failed with status: {prediction_request.status}")
        
        # Добавляем в историю пользователя
        user.add_to_prediction_history(prediction_request)
        
        # Проверяем баланс
        print(f"Remaining balance: {account_manager.get_balance(user.id)}")
        
        # Показываем историю транзакций
        transactions = account_manager.get_transaction_history(user.id)
        print(f"Transaction history: {len(transactions)} transactions")
        
        # Показываем историю предсказаний
        predictions = user.get_prediction_history()
        print(f"Prediction history: {len(predictions)} predictions")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()