import logging
import os
import sys

from flask_cors import CORS

from flask import Flask, g, jsonify, request, send_from_directory

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import project modules
from common_utils.validation import (  # noqa: E402
    sanitize_input,
    validate_dict,
    validate_email,
    validate_integer,
    validate_list,
    validate_request,
    validate_string,
)
from users.auth import create_session_for_user  # noqa: E402
from users.middleware import audit_log, authenticate, require_permission  # noqa: E402
from users.models import UserCreate, UserUpdate  # noqa: E402
from users.password_reset import generate_password_reset_token, reset_password  # noqa: E402
from users.rate_limiting import rate_limit_login, record_login_attempt  # noqa: E402
from users.services import (  # noqa: E402
    authenticate_user,
    create_user,
    get_user_by_id,
    list_users,
    update_user,
)
from users.session_management import (  # noqa: E402
    create_session,
    get_user_sessions,
    terminate_all_user_sessions,
    terminate_session,
)
from users.token_refresh import (  # noqa: E402
    blacklist_token,
    create_refresh_token,
    refresh_auth_token,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="react_frontend/build")
CORS(app)  # Enable CORS for all routes


# Serve React frontend
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


# Define validation schemas
LOGIN_SCHEMA = {
    "username": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=3, max_length=50),
    },
    "password": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=6, max_length=100),
    },
    "remember_me": {"validator": lambda v: isinstance(v, bool)},
}

REGISTER_SCHEMA = {
    "username": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=3, max_length=50),
    },
    "email": {"required": True, "validator": validate_email},
    "password": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=8, max_length=100),
    },
    "name": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=1, max_length=100),
    },
}

PROFILE_UPDATE_SCHEMA = {
    "email": {"validator": validate_email},
    "name": {"validator": lambda v: validate_string(v, min_length=1, max_length=100)},
}

PASSWORD_RESET_REQUEST_SCHEMA = {"email": {"required": True, "validator": validate_email}}

PASSWORD_RESET_SCHEMA = {
    "token": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=10),
    },
    "password": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=8, max_length=100),
    },
}

PASSWORD_CHANGE_SCHEMA = {
    "current_password": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=6),
    },
    "new_password": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=8, max_length=100),
    },
}

TOKEN_REFRESH_SCHEMA = {
    "refresh_token": {
        "required": True,
        "validator": lambda v: validate_string(v, min_length=10),
    }
}

SOLUTION_GENERATION_SCHEMA = {
    "nicheId": {"required": True, "validator": validate_integer},
    "templateId": {"required": True, "validator": validate_integer},
}

MONETIZATION_STRATEGY_SCHEMA = {
    "solutionId": {"required": True, "validator": validate_integer},
    "options": {"validator": validate_dict},
}

MARKETING_CAMPAIGN_SCHEMA = {
    "solutionId": {"required": True, "validator": validate_integer},
    "audienceIds": {
        "required": True,
        "validator": lambda v: validate_list(v, min_length=1),
    },
    "channelIds": {
        "required": True,
        "validator": lambda v: validate_list(v, min_length=1),
    },
}

NICHE_ANALYSIS_SCHEMA = {
    "segments": {
        "required": True,
        "validator": lambda v: validate_list(v, min_length=1),
    }
}


# Auth endpoints
@app.route("/api/auth/login", methods=["POST"])
@sanitize_input
@validate_request(LOGIN_SCHEMA)
@rate_limit_login
@audit_log("login", "user")
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    remember_me = data.get("remember_me", False)

    # Get client IP for session tracking
    ip_address = request.remote_addr

    # Get device info from user agent
    user_agent = request.headers.get("User-Agent", "")
    device_info = {"user_agent": user_agent}

    # Authenticate user
    user = authenticate_user(username, password)
    if user:
        # Record successful login attempt
        if hasattr(g, "rate_limit_identifiers"):
            record_login_attempt(g.rate_limit_identifiers["username"], True)
            record_login_attempt(g.rate_limit_identifiers["ip"], True)

        # Create auth token
        session_data = create_session_for_user(user)

        # Create refresh token if remember_me is enabled
        if remember_me:
            refresh_token = create_refresh_token(user.id)
            session_data["refresh_token"] = refresh_token

        # Create session record
        create_session(
            user_id=user.id,
            token=session_data["token"],
            device_info=device_info,
            ip_address=ip_address,
        )

        return jsonify(session_data), 200

    return (
        jsonify({"error": "Authentication Error", "message": "Invalid credentials"}),
        401,
    )


@app.route("/api/auth/logout", methods=["POST"])
@authenticate
@audit_log("logout", "user")
def logout():
    # Get the token from the Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ")[1]
        # Blacklist the token
        blacklist_token(token)

    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/api/auth/register", methods=["POST"])
@sanitize_input
@validate_request(REGISTER_SCHEMA)
@audit_log("register", "user")
def register():
    try:
        data = request.json
        user_data = UserCreate(
            username=data.get("username"),
            email=data.get("email"),
            name=data.get("name"),
            password=data.get("password"),
        )

        # Create user with default 'user' role
        user = create_user(user_data)

        # Create session
        session_data = create_session_for_user(user)

        # Get client IP for session tracking
        ip_address = request.remote_addr

        # Get device info from user agent
        user_agent = request.headers.get("User-Agent", "")
        device_info = {"user_agent": user_agent}

        # Create session record
        create_session(
            user_id=user.id,
            token=session_data["token"],
            device_info=device_info,
            ip_address=ip_address,
        )

        return jsonify(session_data), 201
    except ValueError as e:
        return jsonify({"error": "Validation Error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"User registration error: {str(e)}")
        return jsonify({"error": "Server Error", "message": "Registration failed"}), 500


@app.route("/api/auth/refresh", methods=["POST"])
@sanitize_input
@validate_request(TOKEN_REFRESH_SCHEMA)
@audit_log("refresh_token", "user")
def refresh_token():
    data = request.json
    refresh_token_str = data.get("refresh_token")

    # Refresh the auth token
    result = refresh_auth_token(refresh_token_str)
    if result:
        return jsonify(result), 200

    return (
        jsonify(
            {
                "error": "Authentication Error",
                "message": "Invalid or expired refresh token",
            }
        ),
        401,
    )


@app.route("/api/auth/password/reset-request", methods=["POST"])
@sanitize_input
@validate_request(PASSWORD_RESET_REQUEST_SCHEMA)
@audit_log("password_reset_request", "user")
def request_password_reset():
    data = request.json
    email = data.get("email")

    # Generate password reset token
    result = generate_password_reset_token(email)

    # Always return success to prevent email enumeration
    # In a real app, you would send an email with the reset link
    if result:
        token, expiry = result
        logger.info(f"Password reset token generated for {email}: {token}")
        # Here you would send an email with the reset link
        # For demo purposes, we'll just log it

    return (
        jsonify(
            {"message": "If your email is registered, you will receive a password reset link."}
        ),
        200,
    )


@app.route("/api/auth/password/reset", methods=["POST"])
@sanitize_input
@validate_request(PASSWORD_RESET_SCHEMA)
@audit_log("password_reset", "user")
def reset_password_endpoint():
    data = request.json
    token = data.get("token")
    new_password = data.get("password")

    # Reset the password
    success = reset_password(token, new_password)
    if success:
        return (
            jsonify({"message": "Password reset successful."}),
            200,
        )

    return (
        jsonify(
            {
                "error": "Reset Error",
                "message": "Invalid or expired token. Please request a new password reset.",
            }
        ),
        400,
    )


@app.route("/api/auth/password/change", methods=["POST"])
@authenticate
@sanitize_input
@validate_request(PASSWORD_CHANGE_SCHEMA)
@audit_log("password_change", "user")
def change_password():
    data = request.json
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    # Verify current password
    user = authenticate_user(g.user.username, current_password)
    if not user:
        return (
            jsonify(
                {
                    "error": "Authentication Error",
                    "message": "Current password is incorrect",
                }
            ),
            401,
        )

    try:
        # Update password
        user_data = UserUpdate(password=new_password)
        updated_user = update_user(g.user_id, user_data)

        if not updated_user:
            return (
                jsonify({"error": "Server Error", "message": "Failed to update password"}),
                500,
            )

        # Terminate all other sessions for security
        terminate_all_user_sessions(g.user_id)

        return (
            jsonify(
                {"message": "Password changed successfully. Please log in with your new password."}
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"error": "Validation Error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return (
            jsonify({"error": "Server Error", "message": "Failed to change password"}),
            500,
        )


@app.route("/api/user/profile", methods=["GET"])
@authenticate
def get_profile():
    # The user object is attached to the request by the authenticate middleware
    user = g.user

    # Create session data which includes the public user data
    session_data = create_session_for_user(user)
    return jsonify(session_data["user"]), 200


@app.route("/api/user/sessions", methods=["GET"])
@authenticate
@audit_log("view", "user_sessions")
def get_user_sessions_endpoint():
    """Get all active sessions for the current user."""
    try:
        # Get all sessions for the current user
        sessions = get_user_sessions(g.user_id)

        # Convert sessions to a list of dictionaries for JSON response
        session_list = []
        for session in sessions:
            session_dict = session.to_dict()
            # Remove sensitive data
            if "token" in session_dict:
                del session_dict["token"]
            session_list.append(session_dict)

        return jsonify(session_list), 200
    except Exception as e:
        logger.error(f"Get user sessions error: {str(e)}")
        return (
            jsonify({"error": "Server Error", "message": "Failed to retrieve sessions"}),
            500,
        )


@app.route("/api/user/sessions/<session_id>", methods=["DELETE"])
@authenticate
@audit_log("terminate", "user_session")
def terminate_session_endpoint(session_id):
    """Terminate a specific session."""
    try:
        # Get all sessions for the current user
        sessions = get_user_sessions(g.user_id)

        # Check if the session belongs to the current user
        session_belongs_to_user = False
        for session in sessions:
            if session.id == session_id:
                session_belongs_to_user = True
                break

        if not session_belongs_to_user:
            return jsonify({"error": "Not Found", "message": "Session not found"}), 404

        # Terminate the session
        success = terminate_session(session_id)
        if success:
            return jsonify({"message": "Session terminated successfully"}), 200
        else:
            return (
                jsonify({"error": "Server Error", "message": "Failed to terminate session"}),
                500,
            )
    except Exception as e:
        logger.error(f"Terminate session error: {str(e)}")
        return (
            jsonify({"error": "Server Error", "message": "Failed to terminate session"}),
            500,
        )


@app.route("/api/user/sessions", methods=["DELETE"])
@authenticate
@audit_log("terminate_all", "user_sessions")
def terminate_all_sessions_endpoint():
    """Terminate all sessions for the current user except the current one."""
    try:
        # Get the current session ID from the request
        auth_header = request.headers.get("Authorization", "")
        current_session_id = None

        if auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
            # Find the session with this token
            sessions = get_user_sessions(g.user_id)
            for session in sessions:
                if session.token == token:
                    current_session_id = session.id
                    break

        # Terminate all sessions except the current one
        count = terminate_all_user_sessions(g.user_id, current_session_id)

        return (
            jsonify({"message": f"Successfully terminated {count} sessions", "count": count}),
            200,
        )
    except Exception as e:
        logger.error(f"Terminate all sessions error: {str(e)}")
        return (
            jsonify({"error": "Server Error", "message": "Failed to terminate sessions"}),
            500,
        )


@app.route("/api/user/profile", methods=["PUT"])
@authenticate
@sanitize_input
@validate_request(PROFILE_UPDATE_SCHEMA)
@audit_log("update", "user_profile")
def update_profile():
    try:
        data = request.json
        user_data = UserUpdate(email=data.get("email"), name=data.get("name"))

        # Update user
        user = update_user(g.user_id, user_data)
        if not user:
            return jsonify({"error": "Not Found", "message": "User not found"}), 404

        # Create session data which includes the public user data
        session_data = create_session_for_user(user)
        return jsonify(session_data["user"]), 200
    except ValueError as e:
        return jsonify({"error": "Validation Error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"User profile update error: {str(e)}")
        return (
            jsonify({"error": "Server Error", "message": "Profile update failed"}),
            500,
        )


# User management (admin only)
@app.route("/api/users", methods=["GET"])
@authenticate
@require_permission("user:view")
def get_users():
    try:
        skip = request.args.get("skip", default=0, type=int)
        limit = request.args.get("limit", default=100, type=int)

        users = list_users(skip=skip, limit=limit)
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        return (
            jsonify({"error": "Server Error", "message": "Failed to retrieve users"}),
            500,
        )


@app.route("/api/users/<user_id>", methods=["GET"])
@authenticate
@require_permission("user:view")
def get_user(user_id):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "Not Found", "message": "User not found"}), 404

        # Create a public user object without sensitive data
        session_data = create_session_for_user(user)
        return jsonify(session_data["user"]), 200
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return (
            jsonify({"error": "Server Error", "message": "Failed to retrieve user"}),
            500,
        )


# Niche Analysis endpoints
@app.route("/api/niche-analysis/segments", methods=["GET"])
@authenticate
def get_market_segments():
    # Mock data - in production, this would come from a database
    segments = [
        {"id": 1, "name": "E-commerce"},
        {"id": 2, "name": "Content Creation"},
        {"id": 3, "name": "Software Development"},
        {"id": 4, "name": "Education"},
        {"id": 5, "name": "Healthcare"},
        {"id": 6, "name": "Finance"},
        {"id": 7, "name": "Marketing"},
        {"id": 8, "name": "Legal"},
        {"id": 9, "name": "Real Estate"},
        {"id": 10, "name": "Hospitality"},
        {"id": 11, "name": "Manufacturing"},
        {"id": 12, "name": "Retail"},
        {"id": 13, "name": "Transportation"},
    ]
    return jsonify(segments), 200


@app.route("/api/niche-analysis/analyze", methods=["POST"])
@authenticate
@require_permission("niche:create")
@sanitize_input
@validate_request(NICHE_ANALYSIS_SCHEMA)
@audit_log("analyze", "niche")
def analyze_niches():
    data = request.json
    # Get segments but not using them in this mock implementation
    _ = data.get("segments", [])

    try:
        # Here we'd call our actual niche analysis logic
        # For now, return mock data
        analysis_id = "analysis123"
        return jsonify({"analysisId": analysis_id, "message": "Analysis started"}), 202
    except Exception as e:
        return (
            jsonify({"error": "Processing Error", "message": f"Analysis failed: {str(e)}"}),
            500,
        )


@app.route("/api/niche-analysis/results/<analysis_id>", methods=["GET"])
@authenticate
@require_permission("niche:view")
def get_niche_results(analysis_id):
    # Validate the analysis_id format
    # (simple validation for demo purposes - in production you'd check if it exists in database)
    if not isinstance(analysis_id, str) or not analysis_id:
        return (
            jsonify({"error": "Validation Error", "message": "Invalid analysis ID"}),
            400,
        )

    # Mock data - in production, this would retrieve actual analysis results
    results = {
        "analysisId": analysis_id,
        "completed": True,
        "niches": [
            {
                "id": 1,
                "name": "AI-powered content optimization",
                "segment": "Content Creation",
                "opportunityScore": 0.87,
                "competitionLevel": "Medium",
                "demandLevel": "High",
                "profitPotential": 0.85,
                "problems": [
                    "Content creators struggle with SEO optimization",
                    "Manual keyword research is time-consuming",
                    "Difficulty in maintaining voice consistency",
                ],
            },
            {
                "id": 2,
                "name": "Local AI code assistant",
                "segment": "Software Development",
                "opportunityScore": 0.92,
                "competitionLevel": "Low",
                "demandLevel": "Very High",
                "profitPotential": 0.90,
                "problems": [
                    "Privacy concerns with cloud-based coding assistants",
                    "Need for offline coding support",
                    "Customized code suggestions for specific frameworks",
                ],
            },
            {
                "id": 3,
                "name": "AI-powered financial analysis",
                "segment": "Finance",
                "opportunityScore": 0.75,
                "competitionLevel": "High",
                "demandLevel": "High",
                "profitPotential": 0.82,
                "problems": [
                    "Complex data interpretation requires expertise",
                    "Real-time financial decision support is limited",
                    "Personalized investment strategies are expensive",
                ],
            },
        ],
    }
    return jsonify(results), 200


# Developer endpoints
@app.route("/api/developer/niches", methods=["GET"])
@authenticate
@require_permission("solution:view")
def get_niches():
    # Mock data - these would normally be from past niche analyses
    niches = [
        {
            "id": 1,
            "name": "AI-powered content optimization",
            "segment": "Content Creation",
            "opportunityScore": 0.87,
        },
        {
            "id": 2,
            "name": "Local AI code assistant",
            "segment": "Software Development",
            "opportunityScore": 0.92,
        },
        {
            "id": 3,
            "name": "AI-powered financial analysis",
            "segment": "Finance",
            "opportunityScore": 0.75,
        },
    ]
    return jsonify(niches), 200


@app.route("/api/developer/templates", methods=["GET"])
@authenticate
@require_permission("solution:view")
def get_templates():
    # Mock data for solution templates
    templates = [
        {
            "id": 1,
            "name": "Web Application",
            "description": "A web-based tool with responsive design",
            "technologies": ["React", "Node.js", "MongoDB"],
        },
        {
            "id": 2,
            "name": "Desktop Application",
            "description": "A native desktop application with local AI integration",
            "technologies": ["Electron", "Python", "PyTorch"],
        },
        {
            "id": 3,
            "name": "Mobile Application",
            "description": "A cross-platform mobile app",
            "technologies": ["React Native", "Node.js", "SQLite"],
        },
        {
            "id": 4,
            "name": "CLI Tool",
            "description": "A command-line interface tool",
            "technologies": ["Python", "Click", "SQLite"],
        },
    ]
    return jsonify(templates), 200


@app.route("/api/developer/solution", methods=["POST"])
@authenticate
@require_permission("solution:create")
@sanitize_input
@validate_request(SOLUTION_GENERATION_SCHEMA)
@audit_log("create", "solution")
def generate_solution():
    data = request.json
    # Get IDs but not using them in this mock implementation
    _ = data.get("nicheId")
    _ = data.get("templateId")

    try:
        # Here we'd call our actual solution generation logic
        # For now, return a mock response
        solution_id = 12345  # Normally generated or from database
        return (
            jsonify(
                {
                    "solutionId": solution_id,
                    "message": "Solution generated successfully",
                }
            ),
            201,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Processing Error",
                    "message": f"Solution generation failed: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/developer/solutions/<solution_id>", methods=["GET"])
@authenticate
@require_permission("solution:view")
def get_solution_details(solution_id):
    try:
        # Validate the solution_id format
        solution_id = int(solution_id)

        # Mock solution details
        solution = {
            "id": solution_id,
            "name": "AI Content Optimizer Tool",
            "description": "A tool for AI-powered content optimization.",
            "niche": {
                "id": 1,
                "name": "AI-powered content optimization",
                "segment": "Content Creation",
                "opportunityScore": 0.87,
            },
            "template": {
                "id": 1,
                "name": "Web Application",
                "technologies": ["React", "Node.js", "MongoDB"],
            },
            "features": [
                "User authentication and profiles",
                "AI-powered analysis and recommendations",
                "Data visualization dashboard",
                "Custom reporting and exports",
                "API integration capabilities",
            ],
            "technologies": ["React", "Node.js", "MongoDB"],
            "architecture": {
                "frontend": "React",
                "backend": "Node.js",
                "database": "MongoDB",
                "aiModels": [
                    "Transformer-based model",
                    "Fine-tuned for specific domain",
                ],
            },
            "deploymentOptions": [
                "Self-hosted option",
                "Cloud deployment (AWS, Azure, GCP)",
                "Docker container",
            ],
            "developmentTime": "4-6 weeks",
            "nextSteps": [
                "Set up development environment",
                "Initialize project structure",
                "Integrate AI models",
                "Develop core features",
                "Create user interface",
                "Add authentication and user management",
                "Implement data storage",
                "Test and refine",
            ],
        }
        return jsonify(solution), 200
    except ValueError:
        return (
            jsonify({"error": "Validation Error", "message": "Invalid solution ID format"}),
            400,
        )


@app.route("/api/developer/solutions", methods=["GET"])
@authenticate
@require_permission("solution:view")
def get_all_solutions():
    # Mock data for all solutions
    solutions = [
        {
            "id": 12345,
            "name": "AI Content Optimizer Tool",
            "description": "A powerful tool for content optimization.",
            "niche": "AI-powered content optimization",
            "template": "Web Application",
            "dateCreated": "2025-04-28",
        }
    ]
    return jsonify(solutions), 200


# Monetization endpoints
@app.route("/api/monetization/solutions", methods=["GET"])
@authenticate
def get_monetization_solutions():
    # Mock data - normally these would be solutions from the developer module
    solutions = [
        {
            "id": 12345,
            "name": "AI Content Optimizer Tool",
            "description": "A powerful tool for content optimization.",
            "niche": "AI-powered content optimization",
        }
    ]
    return jsonify(solutions), 200


@app.route("/api/monetization/strategy", methods=["POST"])
@sanitize_input
@validate_request(MONETIZATION_STRATEGY_SCHEMA)
def generate_monetization_strategy():
    data = request.json
    # Get data but not using them in this mock implementation
    _ = data.get("solutionId")
    _ = data.get("options", {})

    try:
        # Here we'd call our actual monetization strategy generation logic
        # For now, return a mock response
        strategy_id = 54321  # Normally generated or from database
        return (
            jsonify(
                {
                    "strategyId": strategy_id,
                    "message": "Strategy generated successfully",
                }
            ),
            201,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Processing Error",
                    "message": f"Strategy generation failed: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/monetization/strategy/<strategy_id>", methods=["GET"])
def get_strategy_details(strategy_id):
    try:
        # Validate the strategy_id format
        strategy_id = int(strategy_id)

        # Mock strategy details
        strategy = {
            "id": strategy_id,
            "solutionId": 12345,
            "solutionName": "AI Content Optimizer Tool",
            "basePrice": 19.99,
            "tiers": [
                {
                    "name": "Free Trial",
                    "price": 0,
                    "billingCycle": "N/A",
                    "features": [
                        "Limited access to basic features",
                        "3 projects",
                        "Community support",
                        "7-day trial period",
                    ],
                },
                {
                    "name": "Basic",
                    "price": 19.99,
                    "billingCycle": "monthly",
                    "features": [
                        "Full access to basic features",
                        "10 projects",
                        "Email support",
                        "Basic analytics",
                    ],
                },
                {
                    "name": "Professional",
                    "price": 49.99,
                    "billingCycle": "monthly",
                    "features": [
                        "Access to all features",
                        "Unlimited projects",
                        "Priority support",
                        "Advanced analytics",
                        "Team collaboration",
                    ],
                    "recommended": True,
                },
                {
                    "name": "Enterprise",
                    "price": "Custom",
                    "billingCycle": "custom",
                    "features": [
                        "Everything in Professional",
                        "Dedicated support",
                        "Custom integrations",
                        "SLA guarantees",
                        "Onboarding assistance",
                    ],
                },
            ],
            "projections": [
                {
                    "userCount": 100,
                    "paidUsers": 5,
                    "monthlyRevenue": 199.95,
                    "annualRevenue": 2399.40,
                    "lifetimeValue": 1799.55,
                },
                {
                    "userCount": 500,
                    "paidUsers": 25,
                    "monthlyRevenue": 999.75,
                    "annualRevenue": 11997.00,
                    "lifetimeValue": 8997.75,
                },
            ],
        }
        return jsonify(strategy), 200
    except ValueError:
        return (
            jsonify({"error": "Validation Error", "message": "Invalid strategy ID format"}),
            400,
        )


@app.route("/api/monetization/strategies", methods=["GET"])
def get_all_strategies():
    # Mock data for all monetization strategies
    strategies = [
        {
            "id": 54321,
            "solutionId": 12345,
            "solutionName": "AI Content Optimizer Tool",
            "basePrice": 19.99,
            "tierCount": 4,
            "dateCreated": "2025-04-28",
        }
    ]
    return jsonify(strategies), 200


# Marketing endpoints
@app.route("/api/marketing/solutions", methods=["GET"])
@authenticate
def get_marketing_solutions():
    # Mock data - normally these would be solutions from the developer module
    solutions = [
        {
            "id": 12345,
            "name": "AI Content Optimizer Tool",
            "description": "A powerful tool for content optimization.",
            "niche": "AI-powered content optimization",
        }
    ]
    return jsonify(solutions), 200


@app.route("/api/marketing/audience-personas", methods=["GET"])
def get_audience_personas():
    # Mock audience personas
    personas = [
        {
            "id": 1,
            "name": "Content Creators",
            "interests": ["SEO", "Writing", "Social Media"],
        },
        {
            "id": 2,
            "name": "Small Business Owners",
            "interests": ["Marketing", "Automation", "Analytics"],
        },
        {
            "id": 3,
            "name": "Software Developers",
            "interests": ["Coding", "Productivity", "AI Tools"],
        },
        {
            "id": 4,
            "name": "Financial Analysts",
            "interests": ["Data Analysis", "Market Trends", "Forecasting"],
        },
        {
            "id": 5,
            "name": "Marketing Professionals",
            "interests": ["Campaign Management", "Analytics", "Content Creation"],
        },
    ]
    return jsonify(personas), 200


@app.route("/api/marketing/channels", methods=["GET"])
def get_marketing_channels():
    # Mock marketing channels
    channels = [
        {
            "id": 1,
            "name": "Social Media",
            "platforms": ["Twitter", "LinkedIn", "Facebook", "Instagram"],
        },
        {
            "id": 2,
            "name": "Email Marketing",
            "platforms": ["Newsletters", "Drip Campaigns", "Announcements"],
        },
        {
            "id": 3,
            "name": "Content Marketing",
            "platforms": ["Blog Posts", "Tutorials", "eBooks", "Webinars"],
        },
        {
            "id": 4,
            "name": "Paid Advertising",
            "platforms": ["Google Ads", "Facebook Ads", "LinkedIn Ads"],
        },
        {
            "id": 5,
            "name": "Community Engagement",
            "platforms": ["Reddit", "Discord", "Forums", "Q&A Sites"],
        },
    ]
    return jsonify(channels), 200


@app.route("/api/marketing/campaign", methods=["POST"])
@sanitize_input
@validate_request(MARKETING_CAMPAIGN_SCHEMA)
def generate_marketing_campaign():
    data = request.json
    # Get data but not using them in this mock implementation
    _ = data.get("solutionId")
    _ = data.get("audienceIds", [])
    _ = data.get("channelIds", [])

    try:
        # Here we'd call our actual marketing campaign generation logic
        # For now, return a mock response
        campaign_id = 67890  # Normally generated or from database
        return (
            jsonify(
                {
                    "campaignId": campaign_id,
                    "message": "Campaign generated successfully",
                }
            ),
            201,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Processing Error",
                    "message": f"Campaign generation failed: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/marketing/campaign/<campaign_id>", methods=["GET"])
def get_campaign_details(campaign_id):
    try:
        # Validate the campaign_id format
        campaign_id = int(campaign_id)

        # Mock campaign details - this would be a very complex structure in reality
        # Simplified for this example
        campaign = {
            "id": campaign_id,
            "solutionId": 12345,
            "solutionName": "AI Content Optimizer Tool",
            "strategy": {
                "title": "Marketing Strategy for AI Content Optimizer Tool",
                "summary": "Marketing approach targeting Content Creators and Marketing Pros.",
                "keyPoints": [
                    "Focus on solving specific pain points for each audience segment",
                    "Highlight the AI-powered capabilities and unique features",
                    "Emphasize ease of use and quick implementation",
                    "Showcase real-world examples and case studies",
                    "Leverage free trial to demonstrate value",
                ],
                "timeline": "3-month campaign with phased rollout",
            },
            "content": {
                "socialMedia": [
                    {
                        "platform": "Twitter",
                        "posts": [
                            "Tired of manual optimization? Our AI tool automates the process.",
                            "Save hours weekly with AI Content Optimizer. Users report results.",
                            '"I can\'t believe how much time this saves me" - customer quote.',
                        ],
                    },
                    {
                        "platform": "LinkedIn",
                        "posts": [
                            "Introducing AI Content Optimizer: Automate and improve results.",
                            "We analyzed workflows and found the biggest content creation issues.",
                        ],
                    },
                ],
                "emailMarketing": [
                    {
                        "type": "Welcome Email",
                        "subject": "Welcome to AI Content Optimizer! Here's How to Get Started",
                        "content": "Hi [Name],\n\nThanks for signing up for AI Content Optimizer! "
                        "We're excited to have you on board.\n\n...",
                    }
                ],
            },
        }
        return jsonify(campaign), 200
    except ValueError:
        return (
            jsonify({"error": "Validation Error", "message": "Invalid campaign ID format"}),
            400,
        )


@app.route("/api/marketing/campaigns", methods=["GET"])
def get_all_campaigns():
    # Mock data for all marketing campaigns
    campaigns = [
        {
            "id": 67890,
            "solutionId": 12345,
            "solutionName": "AI Content Optimizer Tool",
            "audiences": ["Content Creators", "Marketing Professionals"],
            "channels": ["Social Media", "Email Marketing"],
            "dateCreated": "2025-04-28",
        }
    ]
    return jsonify(campaigns), 200


# Dashboard endpoints
@app.route("/api/dashboard/overview", methods=["GET"])
def get_dashboard_overview():
    # Mock dashboard data
    overview = {
        "projects": [
            {
                "id": 1,
                "name": "AI Writing Assistant",
                "status": "Active",
                "revenue": 1250,
                "subscribers": 48,
                "progress": 100,
            },
            {
                "id": 2,
                "name": "Local Code Helper",
                "status": "In Development",
                "revenue": 0,
                "subscribers": 0,
                "progress": 65,
            },
            {
                "id": 3,
                "name": "Data Analysis Tool",
                "status": "In Research",
                "revenue": 0,
                "subscribers": 0,
                "progress": 25,
            },
        ],
        "totalRevenue": 1250,
        "totalSubscribers": 48,
        "projectCount": 3,
    }
    return jsonify(overview), 200


@app.route("/api/dashboard/revenue", methods=["GET"])
def get_revenue_stats():
    # Mock revenue statistics
    revenue = {
        "monthly": [
            {"month": "Jan", "revenue": 0},
            {"month": "Feb", "revenue": 0},
            {"month": "Mar", "revenue": 450},
            {"month": "Apr", "revenue": 1250},
        ],
        "byProduct": [{"name": "AI Writing Assistant", "revenue": 1250}],
    }
    return jsonify(revenue), 200


@app.route("/api/dashboard/subscribers", methods=["GET"])
def get_subscriber_stats():
    # Mock subscriber statistics
    subscribers = {
        "growth": [
            {"month": "Jan", "subscribers": 0},
            {"month": "Feb", "subscribers": 0},
            {"month": "Mar", "subscribers": 22},
            {"month": "Apr", "subscribers": 48},
        ],
        "byProduct": [{"name": "AI Writing Assistant", "subscribers": 48}],
        "byTier": [
            {"tier": "Basic", "count": 28},
            {"tier": "Professional", "count": 16},
            {"tier": "Enterprise", "count": 4},
        ],
    }
    return jsonify(subscribers), 200


# Global error handler for validation errors
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    # If it's a validation error from our validation system, return formatted response
    if hasattr(e, "to_dict") and callable(getattr(e, "to_dict")):
        return jsonify(e.to_dict()), getattr(e, "http_status", 400)

    # For all other exceptions, return generic server error
    app.logger.error(f"Unhandled exception: {str(e)}")
    return (
        jsonify({"error": "Server Error", "message": "An unexpected error occurred"}),
        500,
    )


if __name__ == "__main__":
    # Use environment variables to configure the server
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    # Always bind to localhost for security
    host = "127.0.0.1"
    port = int(os.environ.get("FLASK_PORT", "5000"))

    app.run(host=host, port=port, debug=debug_mode)
