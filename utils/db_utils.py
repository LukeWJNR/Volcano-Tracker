import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table
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