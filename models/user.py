"""
User authentication and subscription models for the Architectural Design System.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field
from typing import Union
from enum import Enum
import hashlib
import secrets
import json
import os
from pathlib import Path

class SubscriptionPlan(str, Enum):
    """Subscription plan types."""
    BASIC = "basic"
    PRO = "pro"
    ELITE = "elite"

class SubscriptionStatus(str, Enum):
    """Subscription status types."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"

class PlanFeatures(BaseModel):
    """Features available for each subscription plan."""
    max_designs_per_month: int
    can_download_blueprints: bool
    can_access_3d_view: bool
    can_export_multiple_formats: bool
    can_access_analytics: bool
    can_save_designs: bool
    max_saved_designs: int
    priority_support: bool
    advanced_customization: bool
    api_access: bool
    commercial_license: bool

class User(BaseModel):
    """User model with authentication and subscription details."""
    id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    password_hash: str = Field(..., description="Hashed password")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Account active status")
    email_verified: bool = Field(default=False, description="Email verification status")
    
    # Subscription details
    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.BASIC, description="Current subscription plan")
    subscription_status: SubscriptionStatus = Field(default=SubscriptionStatus.TRIAL, description="Subscription status")
    subscription_start_date: Optional[datetime] = Field(None, description="Subscription start date")
    subscription_end_date: Optional[datetime] = Field(None, description="Subscription end date")
    trial_end_date: Optional[datetime] = Field(None, description="Trial period end date")
    
    # Usage tracking
    designs_created_this_month: int = Field(default=0, description="Designs created in current month")
    total_designs_created: int = Field(default=0, description="Total designs created")
    saved_designs: List[str] = Field(default=[], description="List of saved design IDs")

class UserManager:
    """User management system for authentication and subscription handling."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize user manager with data directory."""
        self.data_dir = Path(data_dir)
        self.users_file = self.data_dir / "users.json"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize plan features
        self.plan_features = {
            SubscriptionPlan.BASIC: PlanFeatures(
                max_designs_per_month=5,
                can_download_blueprints=False,
                can_access_3d_view=True,
                can_export_multiple_formats=False,
                can_access_analytics=False,
                can_save_designs=False,
                max_saved_designs=0,
                priority_support=False,
                advanced_customization=False,
                api_access=False,
                commercial_license=False
            ),
            SubscriptionPlan.PRO: PlanFeatures(
                max_designs_per_month=50,
                can_download_blueprints=True,
                can_access_3d_view=True,
                can_export_multiple_formats=True,
                can_access_analytics=True,
                can_save_designs=True,
                max_saved_designs=25,
                priority_support=True,
                advanced_customization=True,
                api_access=False,
                commercial_license=False
            ),
            SubscriptionPlan.ELITE: PlanFeatures(
                max_designs_per_month=999,  # Unlimited
                can_download_blueprints=True,
                can_access_3d_view=True,
                can_export_multiple_formats=True,
                can_access_analytics=True,
                can_save_designs=True,
                max_saved_designs=999,  # Unlimited
                priority_support=True,
                advanced_customization=True,
                api_access=True,
                commercial_license=True
            )
        }
        
        # Load existing users
        self.users = self._load_users()
    
    def _load_users(self) -> dict:
        """Load users from JSON file."""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    return {uid: User(**user_data) for uid, user_data in users_data.items()}
            except Exception as e:
                print(f"Error loading users: {e}")
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file."""
        try:
            users_data = {uid: user.dict() for uid, user in self.users.items()}
            # Convert datetime objects to ISO format strings
            for user_data in users_data.values():
                for field in ['created_at', 'last_login', 'subscription_start_date', 'subscription_end_date', 'trial_end_date']:
                    if user_data.get(field):
                        if isinstance(user_data[field], datetime):
                            user_data[field] = user_data[field].isoformat()
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, hash_value = password_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
        except:
            return False
    
    def create_user(self, email: str, password: str, first_name: str, last_name: str) -> Optional[User]:
        """Create a new user account."""
        # Check if user already exists
        if self.get_user_by_email(email):
            return None
        
        # Generate user ID
        user_id = secrets.token_urlsafe(16)
        
        # Create user with trial period
        trial_end = datetime.now() + timedelta(days=14)  # 14-day trial
        
        user = User(
            id=user_id,
            email=email,
            password_hash=self._hash_password(password),
            first_name=first_name,
            last_name=last_name,
            trial_end_date=trial_end
        )
        
        self.users[user_id] = user
        self._save_users()
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if user and self._verify_password(password, user.password_hash):
            # Update last login
            user.last_login = datetime.now()
            self._save_users()
            return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def update_subscription(self, user_id: str, plan: SubscriptionPlan, duration_months: int = 1) -> bool:
        """Update user subscription plan."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.subscription_plan = plan
        user.subscription_status = SubscriptionStatus.ACTIVE
        user.subscription_start_date = datetime.now()
        user.subscription_end_date = datetime.now() + timedelta(days=30 * duration_months)
        
        self._save_users()
        return True
    
    def get_plan_features(self, plan: SubscriptionPlan) -> PlanFeatures:
        """Get features for a subscription plan."""
        return self.plan_features[plan]
    
    def can_user_access_feature(self, user: User, feature: str) -> bool:
        """Check if user can access a specific feature."""
        if not user.is_active:
            return False
        
        # Check if subscription is active or in trial
        now = datetime.now()
        if user.subscription_status == SubscriptionStatus.TRIAL:
            if user.trial_end_date and now > user.trial_end_date:
                # Trial expired, downgrade to basic
                user.subscription_status = SubscriptionStatus.EXPIRED
                user.subscription_plan = SubscriptionPlan.BASIC
                self._save_users()
        elif user.subscription_status == SubscriptionStatus.ACTIVE:
            if user.subscription_end_date and now > user.subscription_end_date:
                # Subscription expired
                user.subscription_status = SubscriptionStatus.EXPIRED
                user.subscription_plan = SubscriptionPlan.BASIC
                self._save_users()
        
        features = self.get_plan_features(user.subscription_plan)
        return getattr(features, feature, False)
    
    def increment_design_count(self, user_id: str) -> bool:
        """Increment user's design count for the month."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.designs_created_this_month += 1
        user.total_designs_created += 1
        self._save_users()
        return True
    
    def can_create_design(self, user: User) -> bool:
        """Check if user can create more designs this month."""
        features = self.get_plan_features(user.subscription_plan)
        return user.designs_created_this_month < features.max_designs_per_month

# Global user manager instance
user_manager = UserManager()
