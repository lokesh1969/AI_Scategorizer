import os
import json
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.app.core.config import settings

class DatabaseAdapter:
    def __init__(self):
        self.use_mongo = False
        self.client = None
        self.db = None
        self.sqlite_path = settings.SQLITE_FALLBACK_PATH
        self._init_connection()

    def _init_connection(self):
        try:
            self.client = pymongo.MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=1500)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[settings.DATABASE_NAME]
            self.use_mongo = True
            print(f"[Database] Connected successfully to MongoDB at {settings.MONGODB_URL}")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self.use_mongo = False
            print(f"[Database] MongoDB not available ({e}). Using persistent SQLite document store fallback at {self.sqlite_path}")
            self._init_sqlite()

    def _init_sqlite(self):
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                data TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                category TEXT,
                uploader_id TEXT,
                assigned_department TEXT,
                verification_status TEXT,
                priority_level TEXT,
                data TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                user_email TEXT,
                action TEXT,
                timestamp TEXT,
                data TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id TEXT PRIMARY KEY,
                key TEXT UNIQUE,
                data TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_sqlite_conn(self):
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    # --- USERS ---
    def insert_user(self, user_dict: Dict[str, Any]) -> str:
        if "_id" not in user_dict or not user_dict["_id"]:
            user_dict["_id"] = str(uuid.uuid4())
        
        if self.use_mongo:
            self.db.users.insert_one(user_dict)
            return user_dict["_id"]
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO users (id, email, data, created_at) VALUES (?, ?, ?, ?)",
                (user_dict["_id"], user_dict.get("email"), json.dumps(user_dict), str(user_dict.get("created_at", datetime.now().isoformat())))
            )
            conn.commit()
            conn.close()
            return user_dict["_id"]

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        if self.use_mongo:
            user = self.db.users.find_one({"email": email})
            return user
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()
            return json.loads(row["data"]) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if self.use_mongo:
            return self.db.users.find_one({"_id": user_id})
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            return json.loads(row["data"]) if row else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        if self.use_mongo:
            return list(self.db.users.find())
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM users")
            rows = cursor.fetchall()
            conn.close()
            return [json.loads(row["data"]) for row in rows]

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        if self.use_mongo:
            res = self.db.users.update_one({"_id": user_id}, {"$set": updates})
            return res.modified_count > 0
        else:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            user.update(updates)
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET email = ?, data = ? WHERE id = ?",
                (user.get("email"), json.dumps(user), user_id)
            )
            conn.commit()
            conn.close()
            return True

    # --- DOCUMENTS ---
    def insert_document(self, doc_dict: Dict[str, Any]) -> str:
        if "_id" not in doc_dict or not doc_dict["_id"]:
            doc_dict["_id"] = str(uuid.uuid4())
        
        if self.use_mongo:
            self.db.documents.insert_one(doc_dict)
            return doc_dict["_id"]
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO documents 
                   (id, filename, category, uploader_id, assigned_department, verification_status, priority_level, data, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    doc_dict["_id"],
                    doc_dict.get("original_filename"),
                    doc_dict.get("classification", {}).get("predicted_category"),
                    doc_dict.get("uploader_id"),
                    doc_dict.get("assigned_department"),
                    doc_dict.get("verification_status"),
                    doc_dict.get("priority", {}).get("level"),
                    json.dumps(doc_dict),
                    str(doc_dict.get("upload_timestamp", datetime.now().isoformat()))
                )
            )
            conn.commit()
            conn.close()
            return doc_dict["_id"]

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        if self.use_mongo:
            return self.db.documents.find_one({"_id": doc_id})
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            conn.close()
            return json.loads(row["data"]) if row else None

    def get_documents(self, filter_query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.use_mongo:
            q = filter_query or {}
            return list(self.db.documents.find(q).sort("upload_timestamp", pymongo.DESCENDING))
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM documents ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            docs = [json.loads(row["data"]) for row in rows]
            
            if not filter_query:
                return docs

            filtered = []
            for d in docs:
                match = True
                for k, v in filter_query.items():
                    if k == "uploader_id" and d.get("uploader_id") != v:
                        match = False
                    elif k == "assigned_department" and d.get("assigned_department") != v:
                        match = False
                    elif k == "verification_status" and d.get("verification_status") != v:
                        match = False
                    elif k == "classification.predicted_category" and d.get("classification", {}).get("predicted_category") != v:
                        match = False
                    elif k == "priority.level" and d.get("priority", {}).get("level") != v:
                        match = False
                    elif k == "language" and d.get("language") != v:
                        match = False
                if match:
                    filtered.append(d)
            return filtered

    def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        if self.use_mongo:
            res = self.db.documents.update_one({"_id": doc_id}, {"$set": updates})
            return res.modified_count > 0
        else:
            doc = self.get_document_by_id(doc_id)
            if not doc:
                return False
            
            # Deep merge updates
            for k, v in updates.items():
                if "." in k:
                    parts = k.split(".")
                    target = doc
                    for part in parts[:-1]:
                        if part not in target or not isinstance(target[part], dict):
                            target[part] = {}
                        target = target[part]
                    target[parts[-1]] = v
                else:
                    doc[k] = v

            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE documents SET 
                   category = ?, assigned_department = ?, verification_status = ?, priority_level = ?, data = ?
                   WHERE id = ?""",
                (
                    doc.get("classification", {}).get("predicted_category"),
                    doc.get("assigned_department"),
                    doc.get("verification_status"),
                    doc.get("priority", {}).get("level"),
                    json.dumps(doc),
                    doc_id
                )
            )
            conn.commit()
            conn.close()
            return True

    def delete_document(self, doc_id: str) -> bool:
        if self.use_mongo:
            res = self.db.documents.delete_one({"_id": doc_id})
            return res.deleted_count > 0
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            res = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return res

    # --- AUDIT LOGS ---
    def insert_audit_log(self, log_dict: Dict[str, Any]) -> str:
        if "_id" not in log_dict or not log_dict["_id"]:
            log_dict["_id"] = str(uuid.uuid4())
        if "timestamp" not in log_dict:
            log_dict["timestamp"] = datetime.now().isoformat()
            
        if self.use_mongo:
            self.db.audit_logs.insert_one(log_dict)
            return log_dict["_id"]
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_logs (id, user_email, action, timestamp, data) VALUES (?, ?, ?, ?, ?)",
                (
                    log_dict["_id"],
                    log_dict.get("user_email"),
                    log_dict.get("action"),
                    log_dict.get("timestamp"),
                    json.dumps(log_dict)
                )
            )
            conn.commit()
            conn.close()
            return log_dict["_id"]

    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        if self.use_mongo:
            return list(self.db.audit_logs.find().sort("timestamp", pymongo.DESCENDING).limit(limit))
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            return [json.loads(row["data"]) for row in rows]

    # --- SETTINGS ---
    def get_setting(self, key: str, default: Any = None) -> Any:
        if self.use_mongo:
            res = self.db.settings.find_one({"key": key})
            return res.get("value") if res else default
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row["data"]).get("value", default)
            return default

    def set_setting(self, key: str, value: Any) -> bool:
        doc = {"key": key, "value": value, "updated_at": datetime.now().isoformat()}
        if self.use_mongo:
            self.db.settings.update_one({"key": key}, {"$set": doc}, upsert=True)
            return True
        else:
            conn = self._get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (id, key, data) VALUES (?, ?, ?)",
                (key, key, json.dumps(doc))
            )
            conn.commit()
            conn.close()
            return True

db_adapter = DatabaseAdapter()
