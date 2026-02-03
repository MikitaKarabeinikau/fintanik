from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, select, select
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime
from database.models import Students 
from utils.config import Settings
from database.models import Terms
logger = Settings.LOGGER

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def create_term(weekday: str, start_time: str, end_time: str) -> Terms:
    try:
        session = db.get_session()
        if weekday not in weekdays:
            raise ValueError(f"Invalid weekday: {weekday}. Must be one of {weekdays}.")
        new_term = Terms(
            weekday=weekday,
            start_time=start_time,
            end_time=end_time
        )
        session.add(new_term)
        session.commit()
        logger.info(f"Created new term on {weekday} from {start_time} to {end_time}.")
        return new_term
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating term: {e}")
        raise
    finally:
        session.close()

def get_all_terms() -> list[Terms]:
    try:
        terms = Terms.query.all()
        logger.info(f"Retrieved all terms. Total: {len(terms)}")
        return terms
    except Exception as e:
        logger.error(f"Error retrieving terms: {e}")
        raise

def get_terms_boundaries(weekday: str) -> tuple[str, str]:
    try:
        session = db.get_session()
        term = session.query(Terms).filter_by(weekday=weekday).first()
        if not term:
            raise ValueError(f"No term found for weekday: {weekday}")
        logger.info(f"Retrieved term boundaries for {weekday}: {term.start_time} - {term.end_time}")
        return (term.start_time, term.end_time)
    except Exception as e:
        logger.error(f"Error retrieving term boundaries for {weekday}: {e}")
        raise
    finally:
        session.close()

def get_work_days() -> list[str]:
    try:
        session = db.get_session()
        stmt = select(Terms.weekday).where(Terms.start_time != '00:00', Terms.end_time != '00:00').order_by(Terms.id)
        result = session.execute(stmt).scalars().all()
        logger.info(f"Retrieved work days: {result}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving work days: {e}")
        raise
    finally:
        session.close()

def update_start_time(term_id: int, new_start_time: str) -> Terms:
    try:
        session = db.get_session()
        term = session.query(Terms).get(term_id)
        if not term:
            raise ValueError(f"Term with id {term_id} does not exist.")
        term.start_time = new_start_time
        session.commit()
        logger.info(f"Updated start time for term id {term_id} to {new_start_time}.")
        return term
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating start time: {e}")
        raise
    finally:
        session.close()

def update_end_time(term_id: int, new_end_time: str) -> Terms:
    try:
        session = db.get_session()
        term = session.query(Terms).get(term_id)
        if not term:
            raise ValueError(f"Term with id {term_id} does not exist.")
        term.end_time = new_end_time
        session.commit()
        logger.info(f"Updated end time for term id {term_id} to {new_end_time}.")
        return term
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating end time: {e}")
        raise
    finally:
        session.close()

def get_unset_terms() -> list[Terms]:
    try:
        session = db.get_session()
        stmt = select(Terms).where(Terms.start_time == None, Terms.end_time == None)
        unset_terms = session.execute(stmt).scalars().all()
        logger.info(f"Retrieved unset terms. Total: {len(unset_terms)}")
        logger.debug(f"Unset terms details: {unset_terms}")
        return unset_terms
    except Exception as e:
        logger.error(f"Error retrieving unset terms: {e}")
        raise
    finally:
        session.close()

def update_term(weekday: str, start_time: str, end_time: str) -> Terms:
    try:
        session = db.get_session()
        term = session.query(Terms).filter_by(weekday=weekday).first()
        if not term:
            raise ValueError(f"Term with id {weekday} does not exist.")
        term.start_time = start_time
        term.end_time = end_time
        session.commit()
        logger.info(f"Updated term id {weekday} to start time {start_time} and end time {end_time}.")
        return term
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating term: {e}")
        raise
    finally:
        session.close()