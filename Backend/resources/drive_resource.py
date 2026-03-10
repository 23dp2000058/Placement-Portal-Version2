from flask_restful import Resource
from flask_security import auth_required, roles_required
from flask import jsonify, request
from services.drive_service import DriveService

class AdminDriveManagement(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        """List all drives for Admin Dashboard"""
        # Option to filter for pending drives only via query param
        status_filter = request.args.get('status')
        if status_filter == 'pending':
            drives = DriveService.get_pending_drives()
        else:
            drives = DriveService.get_all_drives()
            
        return jsonify([{
            "drive_id": d.driveid,
            "company_name": d.company.name,
            "status": d.driveapprovalstatus,
            "date": d.drivedate.strftime("%Y-%m-%d"),
            "job_count": len(d.jobs_offered)
        } for d in drives])

    @auth_required('token')
    @roles_required('admin')
    def put(self, drive_id):
        """Update drive state. By default this endpoint approved the drive,
        but if the request body contains a `status` key we forward it to
        DriveService.update_drive_status. This allows admins to mark drives
        closed/completed as well as approve them.
        """
        data = request.get_json() or {}
        new_status = data.get('status')
        if new_status:
            success, message = DriveService.update_drive_status(drive_id, new_status)
            if success:
                return {"message": message}, 200
            # service returns error message for not found or invalid
            return {"message": message}, 404 if message == 'Drive not found' else 400

        # no explicit status, fall back to legacy approve behavior
        if DriveService.approve_drive(drive_id):
            return {"message": f"Drive {drive_id} approved successfully"}, 200
        return {"message": "Drive not found"}, 404

    @auth_required('token')
    @roles_required('admin')
    def delete(self, drive_id):
        """Remove a drive and its associated job postings"""
        if DriveService.delete_drive(drive_id):
            return {"message": "Drive removed successfully"}, 200
        return {"message": "Drive not found"}, 404