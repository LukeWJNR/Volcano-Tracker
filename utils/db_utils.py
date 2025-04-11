import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table, Date, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

# Get database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for our models
Base = declarative_base()

# Define our database models
class FavoriteVolcano(Base):
    """Model for storing user favorite volcanoes"""
    __tablename__ = "favorite_volcanoes"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False)
    volcano_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region = Column(String)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FavoriteVolcano(id={self.id}, volcano_name={self.volcano_name})>"

class SearchHistory(Base):
    """Model for storing user search history"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True)
    search_term = Column(String, nullable=False)
    search_type = Column(String, nullable=False)  # "region", "name", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SearchHistory(id={self.id}, search_term={self.search_term})>"

class UserNote(Base):
    """Model for storing user notes about volcanoes"""
    __tablename__ = "user_notes"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False)
    volcano_name = Column(String, nullable=False)
    note_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserNote(id={self.id}, volcano_name={self.volcano_name})>"

class VolcanoRiskAssessment(Base):
    """Model for storing volcano risk assessment data"""
    __tablename__ = "volcano_risk_assessments"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False, unique=True)
    volcano_name = Column(String, nullable=False)
    risk_factor = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    alert_level = Column(String)
    eruption_risk_score = Column(Float)
    type_risk_score = Column(Float)
    monitoring_risk_score = Column(Float)
    regional_risk_score = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VolcanoRiskAssessment(id={self.id}, volcano_name={self.volcano_name}, risk_level={self.risk_level})>"

class VolcanoMonitoringHistory(Base):
    """Model for storing volcano monitoring history data"""
    __tablename__ = "volcano_monitoring_history"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False)
    volcano_name = Column(String, nullable=False)
    alert_level = Column(String)
    has_insar = Column(Boolean, default=False)
    has_so2 = Column(Boolean, default=False)
    has_lava = Column(Boolean, default=False)
    monitoring_notes = Column(Text)
    event_date = Column(Date, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VolcanoMonitoringHistory(id={self.id}, volcano_name={self.volcano_name}, event_date={self.event_date})>"

class VolcanoCharacteristics(Base):
    """Model for storing detailed volcano characteristics"""
    __tablename__ = "volcano_characteristics"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False, unique=True)
    volcano_name = Column(String, nullable=False)
    type = Column(String)
    elevation = Column(Float)
    last_eruption = Column(String)
    crater_diameter_km = Column(Float)
    edifice_height_m = Column(Float)
    tectonic_setting = Column(String)
    primary_magma_type = Column(String)
    historical_fatalities = Column(Integer)
    significant_eruptions = Column(Text)
    geological_summary = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VolcanoCharacteristics(id={self.id}, volcano_name={self.volcano_name})>"

class VolcanoSatelliteImagery(Base):
    """Model for storing volcano satellite imagery links"""
    __tablename__ = "volcano_satellite_imagery"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False)
    volcano_name = Column(String, nullable=False)
    image_type = Column(String, nullable=False)  # 'InSAR', 'Thermal', 'VIS', etc.
    provider = Column(String)  # 'Sentinel', 'Landsat', etc.
    image_url = Column(String, nullable=False)
    capture_date = Column(Date)
    description = Column(Text)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VolcanoSatelliteImagery(id={self.id}, volcano_name={self.volcano_name}, image_type={self.image_type})>"

class EruptionEvent(Base):
    """Model for storing eruption events"""
    __tablename__ = "eruption_events"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False)
    volcano_name = Column(String, nullable=False)
    eruption_start_date = Column(Date, nullable=False)
    eruption_end_date = Column(Date)
    vei = Column(Integer)  # Volcanic Explosivity Index (0-8)
    eruption_type = Column(String)
    max_plume_height_km = Column(Float)
    lava_flow_area_km2 = Column(Float)
    ashfall_area_km2 = Column(Float)
    fatalities = Column(Integer)
    injuries = Column(Integer)
    economic_damage_usd = Column(BigInteger)
    event_description = Column(Text)
    data_source = Column(String)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EruptionEvent(id={self.id}, volcano_name={self.volcano_name}, eruption_start_date={self.eruption_start_date})>"

class VolcanoSoundPreference(Base):
    """Model for storing user's volcano sound preferences"""
    __tablename__ = "volcano_sound_preferences"
    
    id = Column(Integer, primary_key=True)
    volcano_id = Column(String, nullable=False)
    volcano_name = Column(String, nullable=False)
    user_notes = Column(Text, nullable=True)
    saved_date = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VolcanoSoundPreference(id={self.id}, volcano_name={self.volcano_name})>"

# Create all tables in the database
Base.metadata.create_all(engine)

# Create a session factory
SessionFactory = sessionmaker(bind=engine)

def add_favorite_volcano(volcano_data):
    """
    Add a volcano to favorites
    
    Args:
        volcano_data (dict): Dictionary containing volcano information
        
    Returns:
        FavoriteVolcano: The created favorite volcano object
    """
    session = SessionFactory()
    try:
        # Check if volcano already exists in favorites
        existing = session.query(FavoriteVolcano).filter_by(
            volcano_id=volcano_data['id']
        ).first()
        
        if existing:
            return existing
        
        # Create new favorite volcano
        favorite = FavoriteVolcano(
            volcano_id=volcano_data['id'],
            volcano_name=volcano_data['name'],
            latitude=volcano_data['latitude'],
            longitude=volcano_data['longitude'],
            region=volcano_data.get('region', ''),
            country=volcano_data.get('country', '')
        )
        
        session.add(favorite)
        session.commit()
        return favorite
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def remove_favorite_volcano(volcano_id):
    """
    Remove a volcano from favorites
    
    Args:
        volcano_id (str): ID of the volcano to remove
        
    Returns:
        bool: True if volcano was removed, False otherwise
    """
    session = SessionFactory()
    try:
        favorite = session.query(FavoriteVolcano).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if not favorite:
            return False
        
        session.delete(favorite)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_favorite_volcanoes():
    """
    Get all favorite volcanoes
    
    Returns:
        list: List of favorite volcanoes
    """
    session = SessionFactory()
    try:
        favorites = session.query(FavoriteVolcano).all()
        result = []
        
        for fav in favorites:
            result.append({
                'id': fav.volcano_id,
                'name': fav.volcano_name,
                'latitude': fav.latitude,
                'longitude': fav.longitude,
                'region': fav.region,
                'country': fav.country
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

def is_favorite_volcano(volcano_id):
    """
    Check if a volcano is in favorites
    
    Args:
        volcano_id (str): ID of the volcano to check
        
    Returns:
        bool: True if volcano is in favorites, False otherwise
    """
    session = SessionFactory()
    try:
        favorite = session.query(FavoriteVolcano).filter_by(
            volcano_id=volcano_id
        ).first()
        
        return favorite is not None
    except Exception as e:
        raise e
    finally:
        session.close()

def add_search_history(search_term, search_type):
    """
    Add a search to history
    
    Args:
        search_term (str): The search term
        search_type (str): Type of search ("region", "name", etc.)
        
    Returns:
        SearchHistory: The created search history object
    """
    session = SessionFactory()
    try:
        search = SearchHistory(
            search_term=search_term,
            search_type=search_type
        )
        
        session.add(search)
        session.commit()
        return search
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_search_history(limit=10):
    """
    Get search history
    
    Args:
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of search history items
    """
    session = SessionFactory()
    try:
        history = session.query(SearchHistory).order_by(
            SearchHistory.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for item in history:
            result.append({
                'search_term': item.search_term,
                'search_type': item.search_type,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

def add_user_note(volcano_id, volcano_name, note_text):
    """
    Add a user note about a volcano
    
    Args:
        volcano_id (str): ID of the volcano
        volcano_name (str): Name of the volcano
        note_text (str): The note text
        
    Returns:
        UserNote: The created user note object
    """
    session = SessionFactory()
    try:
        # Check if note already exists
        existing = session.query(UserNote).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if existing:
            # Update existing note
            existing.note_text = note_text
            existing.updated_at = datetime.utcnow()
            session.commit()
            return existing
        
        # Create new note
        note = UserNote(
            volcano_id=volcano_id,
            volcano_name=volcano_name,
            note_text=note_text
        )
        
        session.add(note)
        session.commit()
        return note
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_note(volcano_id):
    """
    Get user note for a volcano
    
    Args:
        volcano_id (str): ID of the volcano
        
    Returns:
        dict: User note information or None if not found
    """
    session = SessionFactory()
    try:
        note = session.query(UserNote).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if not note:
            return None
        
        return {
            'volcano_id': note.volcano_id,
            'volcano_name': note.volcano_name,
            'note_text': note.note_text,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise e
    finally:
        session.close()

def get_all_user_notes():
    """
    Get all user notes
    
    Returns:
        list: List of user notes
    """
    session = SessionFactory()
    try:
        notes = session.query(UserNote).all()
        result = []
        
        for note in notes:
            result.append({
                'volcano_id': note.volcano_id,
                'volcano_name': note.volcano_name,
                'note_text': note.note_text,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

# Risk Assessment Functions
def save_risk_assessment(volcano_data, risk_factor, risk_level, eruption_score=None, 
                        type_score=None, monitoring_score=None, regional_score=None):
    """
    Save risk assessment data for a volcano
    
    Args:
        volcano_data (dict): Dictionary containing volcano information
        risk_factor (float): Risk factor (0-1)
        risk_level (str): Risk level (Low, Moderate, High, Very High)
        eruption_score (float, optional): Eruption risk score
        type_score (float, optional): Volcano type risk score
        monitoring_score (float, optional): Monitoring risk score
        regional_score (float, optional): Regional risk score
    
    Returns:
        VolcanoRiskAssessment: The created/updated risk assessment object
    """
    session = SessionFactory()
    try:
        # Check if risk assessment already exists
        existing = session.query(VolcanoRiskAssessment).filter_by(
            volcano_id=volcano_data['id']
        ).first()
        
        if existing:
            # Update existing assessment
            existing.risk_factor = risk_factor
            existing.risk_level = risk_level
            existing.alert_level = volcano_data.get('alert_level')
            
            if eruption_score is not None:
                existing.eruption_risk_score = eruption_score
            if type_score is not None:
                existing.type_risk_score = type_score
            if monitoring_score is not None:
                existing.monitoring_risk_score = monitoring_score
            if regional_score is not None:
                existing.regional_risk_score = regional_score
                
            existing.last_updated = datetime.utcnow()
            session.commit()
            return existing
        
        # Create new risk assessment
        risk_assessment = VolcanoRiskAssessment(
            volcano_id=volcano_data['id'],
            volcano_name=volcano_data['name'],
            risk_factor=risk_factor,
            risk_level=risk_level,
            alert_level=volcano_data.get('alert_level'),
            eruption_risk_score=eruption_score,
            type_risk_score=type_score,
            monitoring_risk_score=monitoring_score,
            regional_risk_score=regional_score
        )
        
        session.add(risk_assessment)
        session.commit()
        return risk_assessment
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_risk_assessments(limit=100):
    """
    Get all volcano risk assessments
    
    Args:
        limit (int): Maximum number of results to return
    
    Returns:
        list: List of risk assessment data
    """
    session = SessionFactory()
    try:
        assessments = session.query(VolcanoRiskAssessment).order_by(
            VolcanoRiskAssessment.risk_factor.desc()
        ).limit(limit).all()
        
        result = []
        for assessment in assessments:
            result.append({
                'volcano_id': assessment.volcano_id,
                'volcano_name': assessment.volcano_name,
                'risk_factor': assessment.risk_factor,
                'risk_level': assessment.risk_level,
                'alert_level': assessment.alert_level,
                'eruption_risk_score': assessment.eruption_risk_score,
                'type_risk_score': assessment.type_risk_score,
                'monitoring_risk_score': assessment.monitoring_risk_score,
                'regional_risk_score': assessment.regional_risk_score,
                'last_updated': assessment.last_updated.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

def get_volcano_risk_assessment(volcano_id):
    """
    Get risk assessment for a specific volcano
    
    Args:
        volcano_id (str): ID of the volcano
    
    Returns:
        dict: Risk assessment data or None if not found
    """
    session = SessionFactory()
    try:
        assessment = session.query(VolcanoRiskAssessment).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if not assessment:
            return None
        
        return {
            'volcano_id': assessment.volcano_id,
            'volcano_name': assessment.volcano_name,
            'risk_factor': assessment.risk_factor,
            'risk_level': assessment.risk_level,
            'alert_level': assessment.alert_level,
            'eruption_risk_score': assessment.eruption_risk_score,
            'type_risk_score': assessment.type_risk_score,
            'monitoring_risk_score': assessment.monitoring_risk_score,
            'regional_risk_score': assessment.regional_risk_score,
            'last_updated': assessment.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise e
    finally:
        session.close()

def get_highest_risk_volcanoes(limit=10):
    """
    Get the highest risk volcanoes
    
    Args:
        limit (int): Maximum number of results to return
    
    Returns:
        list: List of highest risk volcanoes
    """
    session = SessionFactory()
    try:
        assessments = session.query(VolcanoRiskAssessment).order_by(
            VolcanoRiskAssessment.risk_factor.desc()
        ).limit(limit).all()
        
        result = []
        for assessment in assessments:
            result.append({
                'volcano_id': assessment.volcano_id,
                'volcano_name': assessment.volcano_name,
                'risk_factor': assessment.risk_factor,
                'risk_level': assessment.risk_level,
                'alert_level': assessment.alert_level
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

# Volcano Monitoring History Functions
def add_monitoring_history(volcano_id, volcano_name, event_date, alert_level=None, 
                           has_insar=False, has_so2=False, has_lava=False, notes=None):
    """
    Add a monitoring history entry for a volcano
    
    Args:
        volcano_id (str): ID of the volcano
        volcano_name (str): Name of the volcano
        event_date (date): Date of the monitoring event
        alert_level (str, optional): Alert level at the time of monitoring
        has_insar (bool, optional): Whether InSAR data was available
        has_so2 (bool, optional): Whether SO2 data was available
        has_lava (bool, optional): Whether lava data was available
        notes (str, optional): Notes about the monitoring event
        
    Returns:
        VolcanoMonitoringHistory: The created monitoring history object
    """
    session = SessionFactory()
    try:
        # Check if an entry already exists for this volcano on this date
        existing = session.query(VolcanoMonitoringHistory).filter_by(
            volcano_id=volcano_id,
            event_date=event_date
        ).first()
        
        if existing:
            # Update existing entry
            if alert_level is not None:
                existing.alert_level = alert_level
            existing.has_insar = has_insar
            existing.has_so2 = has_so2
            existing.has_lava = has_lava
            if notes is not None:
                existing.monitoring_notes = notes
                
            session.commit()
            return existing
        
        # Create new monitoring history entry
        history = VolcanoMonitoringHistory(
            volcano_id=volcano_id,
            volcano_name=volcano_name,
            event_date=event_date,
            alert_level=alert_level,
            has_insar=has_insar,
            has_so2=has_so2,
            has_lava=has_lava,
            monitoring_notes=notes
        )
        
        session.add(history)
        session.commit()
        return history
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_volcano_monitoring_history(volcano_id, limit=10):
    """
    Get monitoring history for a specific volcano
    
    Args:
        volcano_id (str): ID of the volcano
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of monitoring history items
    """
    session = SessionFactory()
    try:
        history = session.query(VolcanoMonitoringHistory).filter_by(
            volcano_id=volcano_id
        ).order_by(VolcanoMonitoringHistory.event_date.desc()).limit(limit).all()
        
        result = []
        for item in history:
            result.append({
                'volcano_id': item.volcano_id,
                'volcano_name': item.volcano_name,
                'event_date': item.event_date.strftime('%Y-%m-%d'),
                'alert_level': item.alert_level,
                'has_insar': item.has_insar,
                'has_so2': item.has_so2,
                'has_lava': item.has_lava,
                'monitoring_notes': item.monitoring_notes,
                'recorded_at': item.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

def get_latest_monitoring_data():
    """
    Get the latest monitoring data for all volcanoes
    
    Returns:
        list: List of latest monitoring data for all volcanoes
    """
    session = SessionFactory()
    try:
        # Create a subquery to get the most recent monitoring date for each volcano
        from sqlalchemy import func
        
        subq = session.query(
            VolcanoMonitoringHistory.volcano_id,
            func.max(VolcanoMonitoringHistory.event_date).label('max_date')
        ).group_by(VolcanoMonitoringHistory.volcano_id).subquery('t')
        
        # Join with the main table to get the complete records
        latest = session.query(VolcanoMonitoringHistory).join(
            subq, 
            (VolcanoMonitoringHistory.volcano_id == subq.c.volcano_id) & 
            (VolcanoMonitoringHistory.event_date == subq.c.max_date)
        ).all()
        
        result = []
        for item in latest:
            result.append({
                'volcano_id': item.volcano_id,
                'volcano_name': item.volcano_name,
                'event_date': item.event_date.strftime('%Y-%m-%d'),
                'alert_level': item.alert_level,
                'has_insar': item.has_insar,
                'has_so2': item.has_so2,
                'has_lava': item.has_lava
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

# Volcano Characteristics Functions
def save_volcano_characteristics(volcano_id, volcano_name, characteristics):
    """
    Save or update detailed characteristics for a volcano
    
    Args:
        volcano_id (str): ID of the volcano
        volcano_name (str): Name of the volcano
        characteristics (dict): Dictionary of volcano characteristics
            - type (str): Volcano type
            - elevation (float): Elevation in meters
            - last_eruption (str): Last known eruption date
            - crater_diameter_km (float): Crater diameter in kilometers
            - edifice_height_m (float): Edifice height in meters
            - tectonic_setting (str): Tectonic setting
            - primary_magma_type (str): Primary magma type
            - historical_fatalities (int): Historical fatalities count
            - significant_eruptions (str): Text about significant eruptions
            - geological_summary (str): Geological summary text
            
    Returns:
        VolcanoCharacteristics: The created/updated characteristics object
    """
    session = SessionFactory()
    try:
        # Check if characteristics already exist for this volcano
        existing = session.query(VolcanoCharacteristics).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if existing:
            # Update existing characteristics
            for key, value in characteristics.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
                    
            existing.last_updated = datetime.utcnow()
            session.commit()
            return existing
        
        # Create new characteristics entry
        char_data = {
            'volcano_id': volcano_id,
            'volcano_name': volcano_name
        }
        
        # Add all characteristics from the dictionary
        for key, value in characteristics.items():
            if value is not None:
                char_data[key] = value
        
        characteristics_obj = VolcanoCharacteristics(**char_data)
        
        session.add(characteristics_obj)
        session.commit()
        return characteristics_obj
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_volcano_characteristics(volcano_id):
    """
    Get detailed characteristics for a specific volcano
    
    Args:
        volcano_id (str): ID of the volcano
        
    Returns:
        dict: Volcano characteristics or None if not found
    """
    session = SessionFactory()
    try:
        char = session.query(VolcanoCharacteristics).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if not char:
            return None
        
        return {
            'volcano_id': char.volcano_id,
            'volcano_name': char.volcano_name,
            'type': char.type,
            'elevation': char.elevation,
            'last_eruption': char.last_eruption,
            'crater_diameter_km': char.crater_diameter_km,
            'edifice_height_m': char.edifice_height_m,
            'tectonic_setting': char.tectonic_setting,
            'primary_magma_type': char.primary_magma_type,
            'historical_fatalities': char.historical_fatalities,
            'significant_eruptions': char.significant_eruptions,
            'geological_summary': char.geological_summary,
            'last_updated': char.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise e
    finally:
        session.close()

# Satellite Imagery Functions
def add_satellite_image(volcano_id, volcano_name, image_type, image_url, 
                       provider=None, capture_date=None, description=None):
    """
    Add a satellite image link for a volcano
    
    Args:
        volcano_id (str): ID of the volcano
        volcano_name (str): Name of the volcano
        image_type (str): Type of image ('InSAR', 'Thermal', 'VIS', etc.)
        image_url (str): URL to the satellite image
        provider (str, optional): Provider of the image (Sentinel, Landsat, etc.)
        capture_date (date, optional): Date the image was captured
        description (str, optional): Description of the image
        
    Returns:
        VolcanoSatelliteImagery: The created satellite image object
    """
    session = SessionFactory()
    try:
        # Check if identical image already exists
        existing = session.query(VolcanoSatelliteImagery).filter_by(
            volcano_id=volcano_id,
            image_type=image_type,
            image_url=image_url
        ).first()
        
        if existing:
            # Update existing image if needed
            if provider is not None:
                existing.provider = provider
            if capture_date is not None:
                existing.capture_date = capture_date
            if description is not None:
                existing.description = description
                
            session.commit()
            return existing
        
        # Create new satellite image
        satellite_image = VolcanoSatelliteImagery(
            volcano_id=volcano_id,
            volcano_name=volcano_name,
            image_type=image_type,
            image_url=image_url,
            provider=provider,
            capture_date=capture_date,
            description=description
        )
        
        session.add(satellite_image)
        session.commit()
        return satellite_image
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_volcano_satellite_images(volcano_id):
    """
    Get all satellite images for a specific volcano
    
    Args:
        volcano_id (str): ID of the volcano
        
    Returns:
        list: List of satellite images
    """
    session = SessionFactory()
    try:
        images = session.query(VolcanoSatelliteImagery).filter_by(
            volcano_id=volcano_id
        ).order_by(VolcanoSatelliteImagery.image_type).all()
        
        result = []
        for img in images:
            result.append({
                'id': img.id,
                'volcano_id': img.volcano_id,
                'volcano_name': img.volcano_name,
                'image_type': img.image_type,
                'provider': img.provider,
                'image_url': img.image_url,
                'capture_date': img.capture_date.strftime('%Y-%m-%d') if img.capture_date else None,
                'description': img.description,
                'added_at': img.added_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

def get_satellite_images_by_type(image_type, limit=20):
    """
    Get satellite images of a specific type across all volcanoes
    
    Args:
        image_type (str): Type of image to get ('InSAR', 'Thermal', etc.)
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of satellite images
    """
    session = SessionFactory()
    try:
        images = session.query(VolcanoSatelliteImagery).filter_by(
            image_type=image_type
        ).order_by(VolcanoSatelliteImagery.added_at.desc()).limit(limit).all()
        
        result = []
        for img in images:
            result.append({
                'id': img.id,
                'volcano_id': img.volcano_id,
                'volcano_name': img.volcano_name,
                'image_type': img.image_type,
                'provider': img.provider,
                'image_url': img.image_url,
                'capture_date': img.capture_date.strftime('%Y-%m-%d') if img.capture_date else None,
                'description': img.description
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

# Eruption Event Functions
def add_eruption_event(volcano_id, volcano_name, eruption_start_date, eruption_data=None):
    """
    Add an eruption event for a volcano
    
    Args:
        volcano_id (str): ID of the volcano
        volcano_name (str): Name of the volcano
        eruption_start_date (date): Start date of the eruption
        eruption_data (dict, optional): Additional eruption data
            - eruption_end_date (date): End date of the eruption
            - vei (int): Volcanic Explosivity Index
            - eruption_type (str): Type of eruption
            - max_plume_height_km (float): Maximum plume height in km
            - lava_flow_area_km2 (float): Lava flow area in km²
            - ashfall_area_km2 (float): Ashfall area in km²
            - fatalities (int): Number of fatalities
            - injuries (int): Number of injuries
            - economic_damage_usd (int): Economic damage in USD
            - event_description (str): Description of the event
            - data_source (str): Source of the eruption data
            
    Returns:
        EruptionEvent: The created eruption event object
    """
    session = SessionFactory()
    try:
        # Check if an event already exists for this volcano on this date
        existing = session.query(EruptionEvent).filter_by(
            volcano_id=volcano_id,
            eruption_start_date=eruption_start_date
        ).first()
        
        if existing:
            # Update existing event if needed
            if eruption_data:
                for key, value in eruption_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                
            session.commit()
            return existing
        
        # Create new eruption event
        event_data = {
            'volcano_id': volcano_id,
            'volcano_name': volcano_name,
            'eruption_start_date': eruption_start_date
        }
        
        # Add additional data if provided
        if eruption_data:
            for key, value in eruption_data.items():
                if value is not None:
                    event_data[key] = value
        
        eruption_event = EruptionEvent(**event_data)
        
        session.add(eruption_event)
        session.commit()
        return eruption_event
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_volcano_eruption_history(volcano_id):
    """
    Get eruption history for a specific volcano
    
    Args:
        volcano_id (str): ID of the volcano
        
    Returns:
        list: List of eruption events
    """
    session = SessionFactory()
    try:
        events = session.query(EruptionEvent).filter_by(
            volcano_id=volcano_id
        ).order_by(EruptionEvent.eruption_start_date.desc()).all()
        
        result = []
        for event in events:
            event_dict = {
                'id': event.id,
                'volcano_id': event.volcano_id,
                'volcano_name': event.volcano_name,
                'eruption_start_date': event.eruption_start_date.strftime('%Y-%m-%d'),
                'eruption_end_date': event.eruption_end_date.strftime('%Y-%m-%d') if event.eruption_end_date else None,
                'vei': event.vei,
                'eruption_type': event.eruption_type,
                'max_plume_height_km': event.max_plume_height_km,
                'lava_flow_area_km2': event.lava_flow_area_km2,
                'ashfall_area_km2': event.ashfall_area_km2,
                'fatalities': event.fatalities,
                'injuries': event.injuries,
                'economic_damage_usd': event.economic_damage_usd,
                'event_description': event.event_description,
                'data_source': event.data_source
            }
            result.append(event_dict)
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

def get_recent_eruptions(limit=10):
    """
    Get recent eruption events across all volcanoes
    
    Args:
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of recent eruption events
    """
    session = SessionFactory()
    try:
        events = session.query(EruptionEvent).order_by(
            EruptionEvent.eruption_start_date.desc()
        ).limit(limit).all()
        
        result = []
        for event in events:
            result.append({
                'volcano_id': event.volcano_id,
                'volcano_name': event.volcano_name,
                'eruption_start_date': event.eruption_start_date.strftime('%Y-%m-%d'),
                'eruption_end_date': event.eruption_end_date.strftime('%Y-%m-%d') if event.eruption_end_date else 'Ongoing',
                'vei': event.vei,
                'eruption_type': event.eruption_type,
                'fatalities': event.fatalities,
                'event_description': event.event_description
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()

def get_significant_eruptions(min_vei=4):
    """
    Get significant eruption events (with high VEI)
    
    Args:
        min_vei (int): Minimum VEI to consider a significant eruption
        
    Returns:
        list: List of significant eruption events
    """
    session = SessionFactory()
    try:
        events = session.query(EruptionEvent).filter(
            EruptionEvent.vei >= min_vei
        ).order_by(EruptionEvent.vei.desc()).all()
        
        result = []
        for event in events:
            result.append({
                'volcano_id': event.volcano_id,
                'volcano_name': event.volcano_name,
                'eruption_start_date': event.eruption_start_date.strftime('%Y-%m-%d'),
                'vei': event.vei,
                'eruption_type': event.eruption_type,
                'fatalities': event.fatalities,
                'event_description': event.event_description
            })
        
        return result
    except Exception as e:
        raise e
    finally:
        session.close()
# Sound Profile Functions
def add_volcano_sound_preference(volcano_id, volcano_name, user_notes=None):
    """
    Add a volcano to sound preferences
    
    Args:
        volcano_id (str): ID of the volcano
        volcano_name (str): Name of the volcano
        user_notes (str, optional): User notes about this sound preference
        
    Returns:
        VolcanoSoundPreference: The created sound preference object
    """
    session = SessionFactory()
    try:
        # Check if volcano already exists in sound preferences
        existing = session.query(VolcanoSoundPreference).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if existing:
            # Update existing preference
            if user_notes is not None:
                existing.user_notes = user_notes
            existing.saved_date = datetime.utcnow()
            session.commit()
            return existing
        
        # Create new sound preference
        preference = VolcanoSoundPreference(
            volcano_id=volcano_id,
            volcano_name=volcano_name,
            user_notes=user_notes
        )
        
        session.add(preference)
        session.commit()
        return preference
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def remove_sound_preference(volcano_id):
    """
    Remove a volcano from sound preferences
    
    Args:
        volcano_id (str): ID of the volcano to remove
        
    Returns:
        bool: True if volcano was removed, False otherwise
    """
    session = SessionFactory()
    try:
        preference = session.query(VolcanoSoundPreference).filter_by(
            volcano_id=volcano_id
        ).first()
        
        if not preference:
            return False
        
        session.delete(preference)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_sound_preferences():
    """
    Get all user's saved sound preferences
    
    Returns:
        list: List of sound preferences, or empty list on error
    """
    session = SessionFactory()
    try:
        preferences = session.query(VolcanoSoundPreference).order_by(
            VolcanoSoundPreference.saved_date.desc()
        ).all()
        
        result = []
        for pref in preferences:
            result.append({
                'volcano_id': pref.volcano_id,
                'volcano_name': pref.volcano_name,
                'user_notes': pref.user_notes,
                'saved_date': pref.saved_date.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return result
    except Exception as e:
        # Log error but don't crash
        print(f"Database error in get_user_sound_preferences: {str(e)}")
        return []
    finally:
        session.close()

def is_sound_preference(volcano_id):
    """
    Check if a volcano is in sound preferences
    
    Args:
        volcano_id (str): ID of the volcano to check
        
    Returns:
        bool: True if volcano is in sound preferences, False otherwise
    """
    if not volcano_id:
        return False
        
    session = SessionFactory()
    try:
        preference = session.query(VolcanoSoundPreference).filter_by(
            volcano_id=volcano_id
        ).first()
        
        return preference is not None
    except Exception as e:
        # Log the error but don't crash the app
        print(f"Database error in is_sound_preference: {str(e)}")
        return False
    finally:
        session.close()
