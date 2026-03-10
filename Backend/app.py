import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore

# Import the Database and Config
from extensions import db
from config import LocalDevelopmentConfig as Config

# Import all models to ensure tables are created correctly
from models import User, Role, Student, Company, Jobposition, Application, Placementdrive

def create_app():
    app = Flask(__name__)
    
    # 1. Load Config
    app.config.from_object(Config)

    # 2. Initialize Extensions
    CORS(app) 
    db.init_app(app)
    # Define api locally within the app context
    api = Api(app)
    
    # 3. Setup Flask-Security-Too
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)

    # 4. Register Authentication Blueprint
    from resources.auth_resource import auth_bp
    app.register_blueprint(auth_bp)

    # 5. Register All REST Resources
    from resources.student_resource import (
        StudentDashboard, StudentJobAction, StudentProfile, JobBoardAPI,
        StudentDrivesAPI, StudentAppliedDrivesAPI,
        StudentApplicationHistoryAPI, StudentCheckApplicationAPI, StudentApplyAPI
    )
    from resources.company_resource import (
        CompanyDashboard, CompanyApplicationAction,
        CompanyProfile, CompanyDrivesAPI, CompanyDriveStatusAPI,
        CompanyApplicationsAPI,
        CompanyDeleteDriveAPI, CompanyUpdateApplicationStatusAPI
    )
    from resources.admin_resource import (
        AdminSearch, AdminApplicationMonitoring, CompanyApprovalAPI, BlacklistResource,
        AdminCompaniesResource, AdminStudentsResource, AdminCompanyApplicationsResource,
        AdminCompanyDeleteResource, AdminStudentDeleteResource, AdminCompanyApproveResource
    )
    from resources.drive_resource import AdminDriveManagement
    from resources.drive_detail_resource import DriveDetailAPI
    from resources.application_detail_resource import ApplicationDetailAPI

    # Map URLs to Resource Classes
    # Student Routes
    api.add_resource(StudentDashboard, '/student/dashboard')
    api.add_resource(StudentJobAction, '/student/apply/<string:job_id>')
    api.add_resource(StudentProfile, '/student/profile')
    api.add_resource(StudentDrivesAPI, '/student/drives')
    api.add_resource(StudentAppliedDrivesAPI, '/student/applied-drives')
    api.add_resource(StudentApplicationHistoryAPI, '/student/application-history')
    api.add_resource(StudentCheckApplicationAPI, '/student/check-application/<string:job_id>')
    api.add_resource(StudentApplyAPI, '/student/apply')
    api.add_resource(JobBoardAPI, '/api/student/job-board')

    # Company Routes
    api.add_resource(CompanyDashboard, '/company/dashboard')
    api.add_resource(CompanyApplicationAction, '/company/application/<string:application_id>')
    api.add_resource(CompanyProfile, '/company/profile')
    api.add_resource(CompanyDrivesAPI, '/company/drives', '/api/company/placement-drive')
    api.add_resource(CompanyDriveStatusAPI, '/company/drives/<string:drive_id>/status')
    api.add_resource(CompanyApplicationsAPI, '/company/applications')
    api.add_resource(CompanyDeleteDriveAPI, '/company/drives/<string:drive_id>')
    api.add_resource(CompanyUpdateApplicationStatusAPI, '/company/applications/<string:application_id>')
    
    # Admin Routes
    api.add_resource(AdminSearch, '/admin/search/<string:target>')
    api.add_resource(AdminApplicationMonitoring, '/admin/applications', '/admin/student-applications')
    api.add_resource(AdminDriveManagement, '/admin/drive', '/admin/drive/<string:drive_id>')
    api.add_resource(CompanyApprovalAPI, '/admin/approve/company/<string:company_id>')
    api.add_resource(AdminCompaniesResource, '/admin/companies')
    api.add_resource(AdminStudentsResource, '/admin/students')
    api.add_resource(AdminCompanyApplicationsResource, '/admin/company-applications')
    api.add_resource(AdminCompanyDeleteResource, '/admin/company/<string:company_id>')
    api.add_resource(AdminStudentDeleteResource, '/admin/student/<string:student_id>')
    api.add_resource(AdminCompanyApproveResource, '/admin/company-application/<string:application_id>/approve')
    api.add_resource(BlacklistResource, '/admin/blacklist/<string:entity_type>/<string:entity_id>')
    
    # Drive and Application Details
    api.add_resource(DriveDetailAPI, '/drive/<string:drive_id>')
    api.add_resource(ApplicationDetailAPI, '/application/<string:application_id>')

    return app

if __name__ == "__main__":
    app = create_app()
    
    # Auto-create the upload folders
    with app.app_context():
        os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
        os.makedirs(app.config.get('UPLOAD_FOLDER_RESUMES', 'uploads/resumes'), exist_ok=True)
    
    app.run(debug=True)