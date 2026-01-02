from .product import ProductSchema
from .org import OrganizationSchema
from .review import ReviewSchema
from .article import ArticleSchema
from .bread_crumb import BreadCrumbSchema
from .image_meta import ImageMetaSchema
from .local_biz import LocalBusinessSchema
from .video import VideoSchema

SCHEMA_MAP = {
    "Product": ProductSchema,
    "Organization": OrganizationSchema,
    "Review": ReviewSchema,
    "Article": ArticleSchema,
    "Breadcrumb": BreadCrumbSchema,
    "ImageMeta": ImageMetaSchema,
    "LocalBusiness": LocalBusinessSchema,
    "Video": VideoSchema,
}