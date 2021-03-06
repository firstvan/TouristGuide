from datetime import datetime, timedelta

from app import database
from app.db.models import Registration, User

class RegistrationDAO(object):
    @staticmethod
    def get_registration_count_by_tour_id(id_):
        return Registration.query.filter_by(tour_id=id_).count()

    @staticmethod
    def get_tour_users_email(tourid):
        list_of_id = database.session.query(Registration, "user_id").filter_by(
            tour_id=tourid).all()
        ret_list = []
        for id_ in list_of_id:
            ret_list.append(database.session.query(User, "email").filter_by(
                id=id_[1]).first()[1])

        return ret_list

    @staticmethod
    def get_tour_users_id(tourid):
        list_of_id = database.session.query(Registration.user_id).filter_by(
            tour_id=tourid).all()
     
        ret_list = [x[0] for x in list_of_id]

        return ret_list

    @staticmethod
    def get_registrations_of_user(user):
        return Registration.query.filter_by(user_id=user.id).all()

    @staticmethod 
    def get_registrations_tour_ids_of_user(user):
        return database.session.query(Registration.tour_id).filter(Registration.user==user).all()

    @staticmethod
    def register_user(user, tour):
        registration = Registration.query.filter_by(
            user=user, tour=tour).first()

        active_registration = Registration.query.filter(Registration.user == user).all()
        
        ontour = ""

        for reg in active_registration:
            if reg.tour.start_datetime <= tour.start_datetime <= reg.tour.end_datetime:
                ontour = reg.tour.name
                break

        ontour2 = ""
        
        for reg in active_registration:
            if reg.tour.start_datetime <= tour.end_datetime <= reg.tour.end_datetime:
                ontour2 = reg.tour.name
                break

        last_apply = tour.start_datetime + timedelta(days=-1)
        last_apply = last_apply.replace(hour=12, minute=0, second=0, microsecond=0)
        if last_apply <= datetime.now():
            return (4, "")

        if registration:
            return (1, "")
        elif ontour != "":
            return (2, ontour)
        elif ontour2 != "":
            return (3, ontour2)
        else:
            database.session.add(
                Registration(user, tour, datetime.now(), False))
            database.session.commit()
            return (0, "")

    @staticmethod
    def unregister_user(user_id, tour):
        last_apply = tour.start_datetime + timedelta(days=-1)
        last_apply = last_apply.replace(hour=12, minute=0, second=0, microsecond=0)
        if last_apply <= datetime.now():
            return False 

        Registration.query.filter_by(tour_id=tour.id, user_id=user_id).delete()
        database.session.commit()

        return True

    @staticmethod
    def check_registrated(user_, tour_):
        if Registration.query.filter_by(tour=tour_, user=user_).first()  is not None:
            return True

        return False

    @staticmethod
    def delete_tour(tour_id):
        Registration.query.filter_by(tour_id=tour_id).delete()