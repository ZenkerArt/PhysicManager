import json
from typing import Any

import bpy
from mathutils import Vector
from .utils import get_cloth


def bpy_struct_to_dict(struct: bpy.types.bpy_struct,
                       ignore: list[str] = None,
                       recursion_max: int = 2,
                       recursion_counter: int = 0) -> dict[str, Any]:
    if recursion_counter > recursion_max:
        return {}

    struct_type = struct.bl_rna
    ignore = ignore or []
    dct = {}

    for key in struct_type.properties.keys():
        if any([key.startswith(i) for i in ignore]) or key.startswith('rna'):
            continue
        data = getattr(struct, key, None)

        if isinstance(data, bpy.types.bpy_struct):
            data = bpy_struct_to_dict(data,
                                      ignore=ignore,
                                      recursion_max=recursion_max,
                                      recursion_counter=recursion_counter + 1)
            if not data:
                continue
        if isinstance(data, Vector):
            data = data.to_tuple()

        dct[key] = data

    return dct


def cloth_settings_to_dict(obj: bpy.types.Object):
    cloth = get_cloth(obj)
    dct = bpy_struct_to_dict(cloth.settings, ignore=[
        'rest_shape_key',
        'collection',
        'vertex_group'
    ])
    return dct


class PH_OT_physic_save(bpy.types.Operator):
    bl_label = 'Physic Save'
    bl_idname = 'ph.physic_to_json'

    obj: bpy.props.StringProperty(name='Object Name')

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return get_cloth(context.active_object)

    def execute(self, context: bpy.types.Context):
        obj = bpy.data.objects.get(self.obj) or context.active_object

        bpy.context.window_manager.clipboard = json.dumps(cloth_settings_to_dict(obj), indent=2)
        self.report({'INFO'}, 'Saved To Clipboard')
        return {'FINISHED'}


class PH_OT_physic_load(bpy.types.Operator):
    bl_label = 'Physic Load From File'
    bl_idname = 'ph.json_to_physic'

    obj: bpy.props.StringProperty(name='Object Name')

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return get_cloth(context.active_object)

    def dict_to_bpy_struct(self, struct: bpy.types.bpy_struct, dct: dict[str, Any]) -> dict[str, Any]:
        for key, value in dct.items():
            if isinstance(value, list):
                value = Vector(tuple(value))

            if isinstance(value, dict):
                self.dict_to_bpy_struct(getattr(struct, key), value)
                continue

            setattr(struct, key, value)

    def execute(self, context: bpy.types.Context):
        obj = bpy.data.objects.get(self.obj) or context.active_object
        cloth = get_cloth(obj)
        try:
            obj = json.loads(bpy.context.window_manager.clipboard)
            self.dict_to_bpy_struct(cloth.settings, obj)
        except Exception:
            self.report({'ERROR'}, 'Invalid Json')
            return {'CANCELLED'}
        self.report({'INFO'}, 'Loaded From Clipboard')
        return {'FINISHED'}


class PH_OT_physic_select_all(bpy.types.Operator):
    bl_label = 'Select All'
    bl_idname = 'ph.physic_select_all'

    def execute(self, context: 'Context'):
        for i in context.scene.objects:
            if get_cloth(i) is None:
                continue

            i.select_set(True)
        return {'FINISHED'}


classes = (
    PH_OT_physic_select_all,
    PH_OT_physic_save,
    PH_OT_physic_load,
)
