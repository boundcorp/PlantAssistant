import {FastAdminTable} from "../dev_schema";
import {
  BooleanInput, Create,
  DateInput, EditButton, SimpleForm, TextInput
} from "react-admin";
import * as React from "react";

export function FastAdminCreate({table}: { table: FastAdminTable }) {
  return <Create>
    <SimpleForm>
      {Object.entries(table.pydanticSchema.properties).map(([name, field], index) => {
        if (field.type === 'string') {
          if (field.format === 'date-time')
            return <DateInput name={name} source={name}/>
          return <TextInput name={name} source={name}/>
        }
        if (field.type === 'boolean')
          return <BooleanInput name={name} source={name}/>
      })}
      <EditButton/>

    </SimpleForm>

  </Create>
}