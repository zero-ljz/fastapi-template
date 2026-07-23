

export interface paths {
    "/api/v1/login/access-token": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** 登录获取令牌 */
        post: operations["login_access_token_api_v1_login_access_token_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/login/refresh": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** 刷新 Access Token */
        post: operations["refresh_access_token_api_v1_login_refresh_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/login/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** 退出当前设备 */
        post: operations["logout_api_v1_login_logout_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/login/logout-all": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** 退出全部设备 */
        post: operations["logout_all_api_v1_login_logout_all_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/users/register": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * 用户注册
         * @description 注册新用户。
         */
        post: operations["register_api_v1_users_register_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/users/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * 获取当前用户信息
         * @description 获取当前登录用户的信息。
         */
        get: operations["get_current_user_info_api_v1_users_me_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * 更新个人信息
         * @description 更新当前登录用户的个人信息。
         */
        patch: operations["update_current_user_api_v1_users_me_patch"];
        trace?: never;
    };
    "/api/v1/users/me/password": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * 修改密码
         * @description 修改当前登录用户的密码。
         */
        patch: operations["update_current_user_password_api_v1_users_me_password_patch"];
        trace?: never;
    };
    "/api/v1/users": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * 用户列表（管理员）
         * @description 获取用户分页列表，仅限管理员。
         */
        get: operations["list_users_api_v1_users_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/users/{user_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * 查询用户（管理员）
         * @description 按编号查询用户，仅限管理员。
         */
        get: operations["get_user_api_v1_users__user_id__get"];
        put?: never;
        post?: never;
        /**
         * 删除用户（管理员）
         * @description 删除用户，仅限管理员。
         */
        delete: operations["delete_user_api_v1_users__user_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * 健康检查
         * @description 返回应用健康状态。
         */
        get: operations["health_check_api_v1_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {

        Body_login_access_token_api_v1_login_access_token_post: {

            grant_type?: string | null;

            username: string;

            password: string;

            scope: string;

            client_id?: string | null;

            client_secret?: string | null;
        };

        HTTPValidationError: {

            detail?: components["schemas"]["ValidationError"][];
        };

        RefreshTokenRequest: {

            refresh_token: string;

            client_type?: string | null;

            device_name?: string | null;
        };

        RevokeTokenRequest: {

            refresh_token: string;
        };

        Token: {

            access_token: string;

            refresh_token?: string | null;

            token_type: string;

            expires_in: number;
        };

        UserCreate: {

            email: string;

            password: string;

            username?: string | null;

            display_name?: string | null;
        };

        UserListResponse: {

            items: components["schemas"]["UserRead"][];

            total: number;

            page: number;

            page_size: number;
        };

        UserRead: {

            id: number;

            email: string;

            username?: string | null;

            display_name?: string | null;

            avatar_url?: string | null;

            email_verified_at?: string | null;

            is_active: boolean;

            is_superuser: boolean;

            last_login_at?: string | null;

            created_at: string;

            updated_at: string;
        };

        UserUpdate: {

            display_name?: string | null;

            email?: string | null;

            avatar_url?: string | null;
        };

        UserUpdatePassword: {

            old_password: string;

            new_password: string;
        };

        ValidationError: {

            loc: (string | number)[];

            msg: string;

            type: string;

            input?: unknown;

            ctx?: Record<string, never>;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    login_access_token_api_v1_login_access_token_post: {
        parameters: {
            query?: never;
            header?: {
                "x-client-type"?: string | null;
                "x-device-name"?: string | null;
            };
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/x-www-form-urlencoded": components["schemas"]["Body_login_access_token_api_v1_login_access_token_post"];
            };
        };
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Token"];
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    refresh_access_token_api_v1_login_refresh_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RefreshTokenRequest"];
            };
        };
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Token"];
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    logout_api_v1_login_logout_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RevokeTokenRequest"];
            };
        };
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    logout_all_api_v1_login_logout_all_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    register_api_v1_users_register_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserCreate"];
            };
        };
        responses: {

            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRead"];
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_current_user_info_api_v1_users_me_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRead"];
                };
            };
        };
    };
    update_current_user_api_v1_users_me_patch: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserUpdate"];
            };
        };
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRead"];
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_current_user_password_api_v1_users_me_password_patch: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserUpdatePassword"];
            };
        };
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_users_api_v1_users_get: {
        parameters: {
            query?: {
                /** @description 页码 */
                page?: number;
                /** @description 每页数量 */
                page_size?: number;
                /** @description 搜索关键字 */
                keyword?: string | null;
                /** @description 启用状态筛选 */
                is_active?: boolean | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserListResponse"];
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_user_api_v1_users__user_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                user_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserRead"];
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_user_api_v1_users__user_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                user_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };

            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    health_check_api_v1_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {

            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
}
