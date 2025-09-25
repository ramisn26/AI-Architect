"""
Authentication routes for user signup, login, and session management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from functools import wraps
import re
from models.user import user_manager, SubscriptionPlan, SubscriptionStatus

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page."""
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validation
        errors = []
        
        if not email or not is_valid_email(email):
            errors.append("Please enter a valid email address")
        
        if not first_name or len(first_name) < 2:
            errors.append("First name must be at least 2 characters long")
        
        if not last_name or len(last_name) < 2:
            errors.append("Last name must be at least 2 characters long")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        is_valid, password_msg = is_valid_password(password)
        if not is_valid:
            errors.append(password_msg)
        
        # Check if user already exists
        if user_manager.get_user_by_email(email):
            errors.append("An account with this email already exists")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/signup.html')
        
        # Create user
        user = user_manager.create_user(email, password, first_name, last_name)
        if user:
            session['user_id'] = user.id
            flash(f'Welcome {first_name}! Your account has been created with a 14-day free trial.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to create account. Please try again.', 'error')
    
    return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = user_manager.authenticate_user(email, password)
        if user:
            session['user_id'] = user.id
            if remember_me:
                session.permanent = True
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """User logout."""
    session.pop('user_id', None)
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('landing_page'))

@auth_bp.route('/dashboard')
def dashboard():
    """User dashboard."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = user_manager.get_user_by_id(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    
    # Get user's plan features
    features = user_manager.get_plan_features(user.subscription_plan)
    
    # Calculate subscription info
    subscription_info = {
        'plan': user.subscription_plan.value.title(),
        'status': user.subscription_status.value.title(),
        'designs_used': user.designs_created_this_month,
        'designs_limit': features.max_designs_per_month,
        'saved_designs': len(user.saved_designs),
        'saved_limit': features.max_saved_designs,
        'trial_end': user.trial_end_date,
        'subscription_end': user.subscription_end_date
    }
    
    return render_template('auth/dashboard.html', 
                         user=user, 
                         features=features, 
                         subscription_info=subscription_info,
                         now=datetime.now)

@auth_bp.route('/subscription')
def subscription():
    """Subscription management page."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = user_manager.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get all plan features for comparison
    all_plans = {}
    for plan in SubscriptionPlan:
        all_plans[plan.value] = {
            'name': plan.value.title(),
            'features': user_manager.get_plan_features(plan),
            'price': get_plan_price(plan),
            'is_current': user.subscription_plan == plan
        }
    
    return render_template('auth/subscription.html', user=user, plans=all_plans)

@auth_bp.route('/upgrade/<plan_name>')
def upgrade_plan(plan_name):
    """Upgrade subscription plan (payment integration disabled for now)."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        plan = SubscriptionPlan(plan_name.lower())
    except ValueError:
        flash('Invalid subscription plan', 'error')
        return redirect(url_for('auth.subscription'))
    
    user = user_manager.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))
    
    # For now, just show upgrade page (payment integration disabled)
    plan_info = {
        'name': plan.value.title(),
        'features': user_manager.get_plan_features(plan),
        'price': get_plan_price(plan)
    }
    
    return render_template('auth/upgrade.html', user=user, plan=plan_info, plan_name=plan_name)

def get_plan_price(plan: SubscriptionPlan) -> dict:
    """Get pricing information for a plan."""
    prices = {
        SubscriptionPlan.BASIC: {'monthly': 0, 'yearly': 0},
        SubscriptionPlan.PRO: {'monthly': 29, 'yearly': 290},
        SubscriptionPlan.ELITE: {'monthly': 99, 'yearly': 990}
    }
    return prices.get(plan, {'monthly': 0, 'yearly': 0})

def login_required(f):
    """Decorator to require login for routes."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user."""
    if 'user_id' in session:
        return user_manager.get_user_by_id(session['user_id'])
    return None
