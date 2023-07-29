import os
import cherrypy
from girder.models.assetstore import Assetstore
from girder.models.setting import Setting
from girder.models.user import User
from girder.exceptions import ValidationException

cherrypy.config["database"]["uri"] = os.getenv("GIRDER_MONGO_URI", "localhost:27017")


ADMIN_USER = os.getenv("GIRDER_ADMIN_USER", "administrator") # Logon is admin
ADMIN_PASS = os.getenv("GIRDER_ADMIN_PASS", "1234") # Password is 1234


def createInitialUser():
    try:
        User().createUser(
            ADMIN_USER,
            ADMIN_PASS,
            ADMIN_USER,
            ADMIN_USER,
            "administrator@localhost",
            admin=True,
            public=True,
        )
    except ValidationException:
        print("Admin user already exists, skipping...")


def createAssetstore():
    try:
        Assetstore().createFilesystemAssetstore("assetstore", "/home/assetstore")
    except ValidationException:
        print("Assetstore already exists, skipping...")


def configure():
    Setting().set(
        "core.cors.allow_origin",
        os.environ.get(
            "CORS_ALLOWED_ORIGINS", "http://localhost:8080, http://localhost:8010"
        ),
    )


def run_girder_init():
    createInitialUser()
    createAssetstore()
    configure()


if __name__ == "__main__":
    run_girder_init()
