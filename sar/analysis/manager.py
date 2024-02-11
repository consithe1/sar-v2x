import sqlite3

class DBManager:
    def __init__(self, db_path: str) -> None:
        self.db = db_path

    def select(self, tables: dict, fields_to_select: list[dict]=None, conditions: list[dict]=None, ordering: list[dict]=None) -> list[tuple]:
        data = None
        
        connexion = sqlite3.connect(self.db)
        cursor = connexion.cursor()

        # create dictionnary with key = table_name and value = table_as
        tables_ids: dict = {}
        from_: dict = tables.get("from_", None)
        inner_join_: list[dict] = tables.get("inner_join_", None)

        if from_ is not None:
            tables_ids[from_.get('table')] = from_.get('as', None)
            if inner_join_ is not None:
                for tab in inner_join_:
                    tables_ids[tab.get('table')] = tab.get('as', None)
            else:
                print("No INNER JOIN elements.")
            
            print(tables_ids)

            sql_command = "SELECT "

            if fields_to_select is not None:
                for field in fields_to_select:
                    f_col = field.get('column')
                    f_tab = field.get('table')
                    f_as = field.get('as', None)

                    # find the corresponding table id in the table_ids dict
                    id_table = tables_ids.get(f_tab)
                    # if the id_table is None, don't add a table identifier before the column selected
                    if id_table is not None:
                        sql_command += f"{id_table}.{f_col}"
                    else:
                        sql_command += f"{f_col}"

                    if f_as is not None:
                        sql_command += f" AS {f_as}, "
                    else:
                        sql_command += ", "
                sql_command = sql_command[:len(sql_command)-2]
            else:
                sql_command += "* "
            sql_command += "\n"

            # add FROM statement
            from_tab = from_.get('table')
            sql_command += f"FROM {from_tab}"
            if tables_ids.get(from_tab) is not None:
                sql_command += f" AS {tables_ids.get(from_tab)}"
            sql_command += '\n'

            # add INNER JOIN statements
            if inner_join_ is not None:
                cpt_inner = 0
                for inner in inner_join_:
                    inner_table = inner.get('table')
                    inner_as = tables_ids.get(inner_table)
                    inner_on = inner.get('on')

                    sql_command += f"INNER JOIN {inner_table}"
                    # add AS identifier if exists
                    if inner_as is not None:
                        sql_command += f" AS {inner_as}"
                    # add ON statement
                    sql_command += " ON "
                    if cpt_inner == 0:
                        # use the FROM table ON attribute
                        prev_inner_table = from_.get('table')
                        prev_inner_as = tables_ids.get(prev_inner_table)
                        prev_inner_on = from_.get('on')
                    else:
                        # use the previous INNER JOIN table ON attribute
                        prev_inner = inner_join_[cpt_inner-1]
                        prev_inner_table = prev_inner.get('table')
                        prev_inner_as = tables_ids.get(prev_inner_table)
                        prev_inner_on = prev_inner.get('on')

                    if prev_inner_as is not None:
                        sql_command += f"{prev_inner_as}"
                    else:
                        sql_command += f"{prev_inner_table}"
                    sql_command += f".{prev_inner_on}="

                    if inner_as is not None:
                        sql_command += f"{inner_as}"
                    else:
                        sql_command += f"{inner_table}"
                    sql_command += f".{inner_on}\n"

                    cpt_inner += 1

            # add WHERE statements if exist
            if conditions is not None:
                sql_command += "WHERE "
                for condition in conditions:
                    if tables_ids.get(condition.get('table')) is not None:
                        sql_command += f"{tables_ids.get(condition.get('table'))}."
                    sql_command += f"{condition.get('col')}="
                    if type(condition.get('value')) is int:
                        sql_command += f"{int(condition.get('value'))}"
                    elif type(condition.get('value')) is float:
                        sql_command += f"{float(condition.get('value'))}"
                    else:
                        sql_command += f"'{condition.get('value')}'"
                    sql_command += " AND "
                sql_command = sql_command[:len(sql_command)-5]

            print(f"SQL COMMAND:\n{sql_command}")

            res = cursor.execute(sql_command)
            data = res.fetchall()
            print(f"# of records returned from the select command: {len(data)}")

            cursor.close()
            connexion.commit()
            connexion.close()
        else:
            print("ERROR - No from_ attribute given in paramater tables.")

        return data