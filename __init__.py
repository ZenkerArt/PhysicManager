from .modules import modules

bl_info = {
    "name": "Physic Manager",
    "author": "Zenker",
    "description": "",
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}


def register():
    for i in modules:
        i.register()


def unregister():
    for i in modules:
        i.unregister()
