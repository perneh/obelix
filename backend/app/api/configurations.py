from fastapi import APIRouter, HTTPException, Query

from app.core import configuration_storage
from app.core.configuration_storage import parse_config_id, validate_slug
from app.models.schemas import ConfigurationScope, MessageConfiguration, MessageTemplate

router = APIRouter(tags=["configurations"])


@router.get("/configurations", response_model=list[MessageConfiguration])
def list_configurations(
    category: int | None = Query(default=None, ge=1, le=255),
    scope: ConfigurationScope | None = Query(default=None),
) -> list[MessageConfiguration]:
    return configuration_storage.list_configurations(
        MessageConfiguration,
        scope=scope,
        category=category,
    )


@router.post("/configurations", response_model=MessageConfiguration)
def save_configuration(config: MessageConfiguration) -> MessageConfiguration:
    try:
        slug = validate_slug(config.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    config.id = slug
    configuration_storage.save_configuration(
        config.scope,
        config.message.category,
        slug,
        config,
    )
    return config


@router.get("/configurations/{config_id:path}", response_model=MessageConfiguration)
def get_configuration(config_id: str) -> MessageConfiguration:
    try:
        scope, category, slug = parse_config_id(config_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        return configuration_storage.load_configuration(
            scope, category, slug, MessageConfiguration
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/configurations/{config_id:path}")
def delete_configuration(config_id: str) -> dict[str, str]:
    try:
        scope, category, slug = parse_config_id(config_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    configuration_storage.delete_configuration(scope, category, slug)
    return {"status": "deleted", "id": config_id}


# Legacy template endpoints
@router.get("/templates", response_model=list[MessageConfiguration])
def list_templates_legacy() -> list[MessageConfiguration]:
    return list_configurations(category=None, scope=None)


@router.post("/templates", response_model=MessageConfiguration)
def create_template_legacy(template: MessageTemplate) -> MessageConfiguration:
    slug = template.id.lower().replace("_", "-")
    try:
        slug = validate_slug(slug)
    except ValueError:
        slug = f"template-{slug}"[:40]

    config = MessageConfiguration(
        id=slug,
        name=template.name,
        description=template.description,
        scope=ConfigurationScope.LOCAL,
        message=template.message,
    )
    return save_configuration(config)


@router.get("/templates/{template_id}", response_model=MessageConfiguration)
def get_template_legacy(template_id: str) -> MessageConfiguration:
    configs = list_configurations(category=None, scope=None)
    for config in configs:
        if config.id == template_id or config.config_id == template_id:
            return config
    raise HTTPException(status_code=404, detail=f"Template {template_id} not found")


@router.delete("/templates/{template_id}")
def delete_template_legacy(template_id: str) -> dict[str, str]:
    configs = list_configurations(category=None, scope=None)
    for config in configs:
        if config.id == template_id:
            return delete_configuration(config.config_id)
    raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
