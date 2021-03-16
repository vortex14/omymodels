import os
from simple_ddl_parser import DDLParser, parse_from_file
from typing import Optional, List, Dict
import omymodels.gino.templates as gt
from omymodels.gino.types import types_mapping, postgresql_dialect, datetime_types


state = set()
postgresql_dialect_cols = set()


def get_tables_information(
    ddl: Optional[str] = None, ddl_file: Optional[str] = None
) -> List[Dict]:
    if not ddl_file and not ddl:
        raise ValueError(
            "You need to provide one of above argument: ddl with string that "
            "contains ddl or ddl_file that contains path to ddl file to parse"
        )
    if ddl:
        tables = DDLParser(ddl).run()
    elif ddl_file:
        tables = parse_from_file(ddl_file)
    return tables


def prepare_column_type(column_data: Dict) -> str:
    
    global postgresql_dialect_cols
    column_data_type = column_data["type"].lower().split('[')[0]
    column_type = types_mapping.get(column_data_type, "OMM_UNMAPPED_TYPE")
    if column_type == 'OMM_UNMAPPED_TYPE':
        print(column_data["type"], 'OMM_UNMAPPED_TYPE')
    if column_type in postgresql_dialect:
        postgresql_dialect_cols.add(column_type)
    column = gt.column_template.format(
        column_name=column_data["name"], column_type=column_type
    )
    if column_data["size"]:
        column += f"({column_data['size']})"
    else:
        column += f"()"
    return column


def prepare_column_default(column_data: Dict, column: str) -> str:
    if isinstance(column_data["default"], str):
        if column_data["type"].upper() in datetime_types:
            if 'now' in column_data["default"]:
                # todo: need to add other popular PostgreSQL & MySQL functions
                column_data["default"] = "func.now()"
                state.add("func")
            elif "'" not in column_data["default"]:
                column_data["default"] = f"'{column_data['default']}'"
        elif 'true' in column_data["default"] and not "'" in column_data["default"]:
            column_data["default"] = True
        elif 'false' in column_data["default"] and not "'" in column_data["default"]:
            column_data["default"] = False
        else:
            if "'" not in column_data["default"]:
                column_data["default"] = f"'{column_data['default']}'"
    column += gt.default.format(default=column_data["default"])
    return column


def setup_column_attributes(column_data: Dict, table_pk: List[str], column: str) -> str:

    if column_data["type"].lower() == "serial" or column_data["type"].lower() == "bigserial":
        column += gt.autoincrement
    if not column_data["nullable"]:
        column += gt.required
    if column_data["default"]:
        column = prepare_column_default(column_data, column)
    if column_data["name"] in table_pk:
        column += gt.pk_template
    return column


def generate_column(column_data: Dict, table_pk: List[str]) -> str:
    """ method to generate full column defention """
    column = setup_column_attributes(
        column_data, table_pk, prepare_column_type(column_data)
    )
    column += ")\n"
    return column


def generate_model(table: Dict) -> str:
    """ method to prepare one Model defention - name & tablename  & columns """
    print(table)
    model = ""
    if table.get('table_name'):
        # mean table
        model = gt.model_template.format(
            model_name=table["table_name"].capitalize(), table_name=table["table_name"]
        )
        for column in table["columns"]:
            model += generate_column(column, table["primary_key"])
    elif table.get('sequence_name'):
        # create sequence
        ...
    return model


def create_header(tables: List[Dict]) -> str:
    """ header of the file - imports & gino init """
    header = ""
    if "func" in state:
        header += gt.sql_alchemy_func_import + "\n"
    print(postgresql_dialect)
    if postgresql_dialect_cols:
        header += gt.postgresql_dialect_import.format(types=",".join(postgresql_dialect_cols)) + "\n"
    header += gt.gino_import + "\n\n"
    if tables[0]["schema"]:
        header += gt.gino_init_schema + "\n"
    else:
        header += gt.gino_init + "\n"
    return header


def generate_gino_models_file(tables: List[Dict]) -> str:
    """ method to prepare full file with all Models &  """
    output = ""
    for table in tables:
        output += generate_model(table)
    header = create_header(tables)
    output = header + output
    return output


def save_models_to_file(models: str, dump_path: str) -> None:
    folder = os.path.dirname(dump_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(dump_path, "w+") as f:
        f.write(models)


def create_gino_models(
    ddl: Optional[str] = None,
    ddl_path: Optional[str] = None,
    dump: bool = True,
    dump_path: str = "models.py",
):
    tables = get_tables_information(ddl, ddl_path)
    output = generate_gino_models_file(tables)
    if dump:
        save_models_to_file(output, dump_path)
    else:
        print(output)
        return output
