import {FastAdminTable} from "../dev_schema";
import {BooleanField, Datagrid, DateField, EditButton, List, TextField} from "react-admin";
import * as React from "react";

export function FastAdminTableList({table}: { table: FastAdminTable }) {
  return <List>
    <Datagrid>
      {Object.entries(table.pydanticSchema.properties).map(([name, field], index) => {
        if (field.type === 'string') {
          if (field.format === 'date-time')
            return <DateField source={name}/>
          return <TextField source={name}/>
        }
        if (field.type === 'boolean')
          return <BooleanField source={name}/>
      })}
      <EditButton/>
    </Datagrid>
  </List>
}