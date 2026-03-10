from flask_restful import Resource
from flask_security import auth_required, roles_accepted
from flask import jsonify
from models import Placementdrive, Jobposition, Application

class DriveDetailAPI(Resource):
    @auth_required('token')
    def get(self, drive_id):
        """Get details of a specific drive"""
        drive = Placementdrive.query.filter_by(driveid=drive_id).first()
        if not drive:
            return {"message": "Drive not found"}, 404
        
        jobs = drive.jobs_offered if drive.jobs_offered else []
        app_count = Application.query.filter(
            Jobposition.drive_id == drive_id
        ).count()
        
        # return plain data; flask-restful will JSONify it
        return {
            "id": drive.driveid,
            "name": jobs[0].title if jobs else "Drive",
            "company_name": drive.company.name,
            "date": drive.drivedate.strftime("%Y-%m-%d"),
            "status": drive.driveapprovalstatus,
            "applicant_count": app_count,
            "position": jobs[0].title if jobs else "N/A",
            "location": jobs[0].job_location if jobs else "N/A",
            "package": float(jobs[0].salary) if jobs and jobs[0].salary else 0,
            "description": jobs[0].job_description if jobs else "No description",
            "qualification": jobs[0].eligible_branches if jobs else "All",
            "experience": "Fresher",
            "cgpa_cutoff": "N/A"
        }, 200
