import strawberry
from typing import Optional, List

@strawberry.type
class Instructor:
    nombre: str

@strawberry.type
class Taller:
    nombre: str
    instructor: Instructor
    cupo: int
    activo: bool

@strawberry.input
class AgregarTallerInput:
    nombre: str
    instructor: str
    cupo: int
    activo: bool

@strawberry.type
class Role:
    id: strawberry.ID
    code: str
    name: str
    is_active: bool

@strawberry.type
class Permission:
    id: strawberry.ID
    code: str
    name: str
    is_active: bool

talleres_db = [
    Taller(nombre="Python para backend", instructor=Instructor(nombre="Ana López"), cupo=20, activo=True)
]

roles_db = [
    Role(id="1", code="ADMINISTRADOR", name="Administrador", is_active=True),
    Role(id="2", code="CONSULTA", name="Consulta", is_active=True)
]

permissions_db = [
    Permission(id="1", code="talleres.write", name="Crear talleres", is_active=True),
    Permission(id="2", code="talleres.read", name="Ver talleres", is_active=True)
]

role_permissions_db = {
    "1": ["1", "2"],
    "2": ["2"]
}

usuarios_roles_db = {
    "user_admin": "1",
    "user_normal": "2"
}

def exigir_permiso(user_id: str, codigo_permiso: str) -> None:
    rol_id = usuarios_roles_db.get(user_id)
    if not rol_id:
        raise Exception("El usuario no tiene un rol activo asignado.")
    
    permisos_del_rol_ids = role_permissions_db.get(rol_id, [])
    permisos_activos = [p.code for p in permissions_db if p.id in permisos_del_rol_ids]
    
    if codigo_permiso not in permisos_activos:
        raise Exception(f"Operación rechazada. Tu rol no tiene el permiso: {codigo_permiso}")

@strawberry.type
class Query:
    @strawberry.field
    def talleres(self) -> List[Taller]:
        return talleres_db

    @strawberry.field
    def roles(self) -> List[Role]:
        return roles_db

    @strawberry.field
    def permissions(self) -> List[Permission]:
        return permissions_db

@strawberry.type
class Mutation:
    @strawberry.mutation
    def agregar_taller(self, taller: AgregarTallerInput, actor_user_id: str) -> Optional[Taller]:
        try:
            exigir_permiso(actor_user_id, "talleres.write")
            
            nuevo_taller = Taller(
                nombre=taller.nombre,
                instructor=Instructor(nombre=taller.instructor),
                cupo=taller.cupo,
                activo=taller.activo,
            )
            talleres_db.append(nuevo_taller)
            return nuevo_taller
            
        except Exception as e:
            print(f"Error de acceso: {e}")
            return None

schema = strawberry.Schema(query=Query, mutation=Mutation)