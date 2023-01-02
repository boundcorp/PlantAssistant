export type PydandicField = {
    title: string;
    type: string;
    description?: string;
    default?: any;
    enum?: any[];
    format?: string;
    readOnly?: boolean,
    nullable?: boolean,
    maxLength?: number,
}
export type PydanticSchema = {
    title: string;
    type: string;
    description?: string;
    additionalProperties?: boolean;
    properties: {
        [key: string]: PydandicField
    }
}

export type FastAdminTable = {
    name: string;
    pydanticSchema: PydanticSchema
}
export const tables = [
    {
        "name": "User",
        "pydanticSchema": {
            "title": "User",
            "description": "The User model",
            "type": "object",
            "properties": {
                "id": {
                    "title": "Id",
                    "type": "string",
                    "format": "uuid"
                },
                "created_at": {
                    "title": "Created At",
                    "readOnly": true,
                    "nullable": true,
                    "type": "string",
                    "format": "date-time"
                },
                "modified_at": {
                    "title": "Modified At",
                    "readOnly": true,
                    "nullable": true,
                    "type": "string",
                    "format": "date-time"
                },
                "email": {
                    "title": "Email",
                    "description": "This is a username",
                    "maxLength": 200,
                    "type": "string"
                }
            },
            "required": [
                "email"
            ],
            "additionalProperties": false
        }
    },
    {
        "name": "Property",
        "pydanticSchema": {
            "title": "Property",
            "description": "The Property model corresponds to a HomeAssistant installation",
            "type": "object",
            "properties": {
                "id": {
                    "title": "Id",
                    "type": "string",
                    "format": "uuid"
                },
                "created_at": {
                    "title": "Created At",
                    "readOnly": true,
                    "nullable": true,
                    "type": "string",
                    "format": "date-time"
                },
                "modified_at": {
                    "title": "Modified At",
                    "readOnly": true,
                    "nullable": true,
                    "type": "string",
                    "format": "date-time"
                },
                "name": {
                    "title": "Name",
                    "maxLength": 255,
                    "nullable": true,
                    "type": "string"
                },
                "homeassistant_url": {
                    "title": "Homeassistant Url",
                    "maxLength": 2048,
                    "nullable": true,
                    "type": "string"
                },
                "homeassistant_token": {
                    "title": "Homeassistant Token",
                    "maxLength": 1024,
                    "nullable": true,
                    "type": "string"
                }
            },
            "additionalProperties": false
        }
    },
] as { name: string; pydanticSchema: PydanticSchema }[]