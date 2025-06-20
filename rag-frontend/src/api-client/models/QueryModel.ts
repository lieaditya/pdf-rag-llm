/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime';
import type { Source } from './Source';
import {
    SourceFromJSON,
    SourceFromJSONTyped,
    SourceToJSON,
    SourceToJSONTyped,
} from './Source';

/**
 * 
 * @export
 * @interface QueryModel
 */
export interface QueryModel {
    /**
     * 
     * @type {string}
     * @memberof QueryModel
     */
    queryId?: string;
    /**
     * 
     * @type {string}
     * @memberof QueryModel
     */
    userId?: string;
    /**
     * 
     * @type {number}
     * @memberof QueryModel
     */
    createdAt?: number;
    /**
     * 
     * @type {number}
     * @memberof QueryModel
     */
    ttl?: number;
    /**
     * 
     * @type {string}
     * @memberof QueryModel
     */
    queryText: string;
    /**
     * 
     * @type {string}
     * @memberof QueryModel
     */
    answerText?: string | null;
    /**
     * 
     * @type {Array<Source>}
     * @memberof QueryModel
     */
    sources?: Array<Source>;
    /**
     * 
     * @type {boolean}
     * @memberof QueryModel
     */
    isComplete?: boolean;
}

/**
 * Check if a given object implements the QueryModel interface.
 */
export function instanceOfQueryModel(value: object): value is QueryModel {
    if (!('queryText' in value) || value['queryText'] === undefined) return false;
    return true;
}

export function QueryModelFromJSON(json: any): QueryModel {
    return QueryModelFromJSONTyped(json, false);
}

export function QueryModelFromJSONTyped(json: any, ignoreDiscriminator: boolean): QueryModel {
    if (json == null) {
        return json;
    }
    return {
        
        'queryId': json['query_id'] == null ? undefined : json['query_id'],
        'userId': json['user_id'] == null ? undefined : json['user_id'],
        'createdAt': json['created_at'] == null ? undefined : json['created_at'],
        'ttl': json['ttl'] == null ? undefined : json['ttl'],
        'queryText': json['query_text'],
        'answerText': json['answer_text'] == null ? undefined : json['answer_text'],
        'sources': json['sources'] == null ? undefined : ((json['sources'] as Array<any>).map(SourceFromJSON)),
        'isComplete': json['is_complete'] == null ? undefined : json['is_complete'],
    };
}

export function QueryModelToJSON(json: any): QueryModel {
    return QueryModelToJSONTyped(json, false);
}

export function QueryModelToJSONTyped(value?: QueryModel | null, ignoreDiscriminator: boolean = false): any {
    if (value == null) {
        return value;
    }

    return {
        
        'query_id': value['queryId'],
        'user_id': value['userId'],
        'created_at': value['createdAt'],
        'ttl': value['ttl'],
        'query_text': value['queryText'],
        'answer_text': value['answerText'],
        'sources': value['sources'] == null ? undefined : ((value['sources'] as Array<any>).map(SourceToJSON)),
        'is_complete': value['isComplete'],
    };
}

