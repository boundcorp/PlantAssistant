import * as React from 'react';
import {useEffect} from 'react';
import {Admin, DataProvider, Resource} from 'react-admin';
import {ApolloClient, gql, InMemoryCache} from '@apollo/client'
import {FastAdminTable, tables} from './dev_schema';
import buildGraphQLProvider, {BuildQueryResult, IntrospectionResult} from 'ra-data-graphql';
import Layout from "./Layout";
import {camelCase} from "lodash"
import {FastAdminTableList} from "./components/TableList";
import {FastAdminCreate} from "./components/Create";

const cache = new InMemoryCache();

const client = new ApolloClient({
    // Provide required constructor fields
    cache: cache,
    uri: 'http://localhost:9988/graphql',

    // Provide some optional constructor fields
    name: 'react-web-client',
    version: '1.3',
    queryDeduplication: false,
    defaultOptions: {
        watchQuery: {
            fetchPolicy: 'cache-and-network',
        },
    },
});

function buildFieldList(introspectionResults: IntrospectionResult, resourceName: string, raFetchType: string) {
    if(resourceName === 'User')
        return ['id', 'email', 'createdAt', 'modifiedAt'];
    else
        return ['id', 'name', 'createdAt', 'modifiedAt', 'homeassistantUrl']
}

const buildQuery = (introspectionResults: IntrospectionResult) => (raFetchType: string, resourceName: string, params: Record<string, any>): BuildQueryResult => {
    let name
    switch (raFetchType) {
        case 'GET_ONE':
            return {
                query: gql`query get_${resourceName}($id: ID) {
                    data: ${resourceName}(id: $id) {
                        ${buildFieldList(introspectionResults, resourceName, raFetchType)}
                    }
                }`,
                variables: params,
                parseResponse: ({data}: { data: any }) => data,
            }
        case 'GET_LIST':
            name = camelCase("list_" + resourceName)
            return {
                query: gql`query ${name} {
                    result: ${name} {
                        total
                        items {
                            ${buildFieldList(introspectionResults, resourceName, raFetchType)}
                        }
                    }
                }`,
                variables: params,
                parseResponse: (response: any) => {
                    const result = response.data.result
                    return {data: result.items, total: result.total}
                },
            }
        case 'CREATE':
            name = camelCase("create_" + resourceName)
            return {
                query: gql`mutation ${name} {
                  result: ${name} {
                    total
                    items {
                      ${buildFieldList(introspectionResults, resourceName, raFetchType)}
                    }
                  }
                }`,
                variables: params,
                parseResponse: (response: any) => {
                    const result = response.data.result
                    return {data: result.items, total: result.total}
                },
            }
    }
    return {} as BuildQueryResult
}

const App = () => {
    const [dataProvider, setDataProvider] = React.useState<DataProvider>();
    useEffect(() => {
        buildGraphQLProvider({client, buildQuery}).then(setDataProvider);
    }, []);

    return <Admin dataProvider={dataProvider} layout={Layout}>
        {tables.map((table) => <Resource name={table.name} key={table.name} {...viewsFor(table)} />)}
    </Admin>
};

export function viewsFor(table: FastAdminTable) {
    return {
        list: <FastAdminTableList table={table}/>,
        create: <FastAdminCreate table={table}/>,
    }
}


export default App