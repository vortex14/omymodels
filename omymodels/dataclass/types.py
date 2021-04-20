import datetime


types_mapping = {
    "varchar": "str",
    "float": "int",
    "integer": "int",
    "date": "datetime.date",
    "timestamp": "datetime.datetime",
    "text": "str",
    "smallint": "int",
    "boolean": "bool",
    "bool": "bool",
    "decimal": "int",
    "bigint": "int",
    "char": "str",
    "time": "datetime.datetime",
    "numeric": "int",
    "character": "str",
    "double": "int",
    "character_vying": "str",
    "varying": "str",
    "serial": "int",
    "jsonb": "Union[dict, list]",
    "json": "Union[dict, list]",
    "int": "int",
    "serial": "int",
    "bigserial": "int",
    "uuid": "UUID",
}



datetime_types = ["TIMESTAMP", "DATETIME", "DATE"]