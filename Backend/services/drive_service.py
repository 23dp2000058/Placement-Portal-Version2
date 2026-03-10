from extensions import db
from models import Placementdrive, Jobposition

class DriveService:
    @staticmethod
    def get_all_drives():
        """Fetch all drives for the Admin to monitor"""
        return Placementdrive.query.all()

    @staticmethod
    def get_pending_drives():
        """NEW: specifically fetch drives awaiting admin approval"""
        return Placementdrive.query.filter_by(driveapprovalstatus='pending').all()

    @staticmethod
    def approve_drive(drive_id_str):
        """Admin approves a drive created by a company"""
        # Lookup using the unique driveid string
        drive = Placementdrive.query.filter_by(driveid=drive_id_str).first()
        if drive:
            drive.driveapprovalstatus = 'approved'
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_drive(drive_id_str):
        """Admin removes a job posting or placement drive"""
        # Lookup using the unique driveid string
        drive = Placementdrive.query.filter_by(driveid=drive_id_str).first()
        if drive:
            # Note: CASCADE delete will handle associated jobs if configured in models
            db.session.delete(drive)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update_drive_status(drive_id_str, new_status):
        """Admin or system-level status change for a drive (approved/closed).
        This does not enforce company ownership and therefore is usable by
        admin users. Returns tuple (success, message)."""
        drive = Placementdrive.query.filter_by(driveid=drive_id_str).first()
        if not drive:
            return False, "Drive not found"
        drive.driveapprovalstatus = new_status
        try:
            db.session.commit()
            return True, "Status updated"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
