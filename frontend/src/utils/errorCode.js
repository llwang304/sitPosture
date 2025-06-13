export const ERROR_CODES = {
  // 通用错误
  SERVER_ERROR: '服务器内部错误',
  BAD_REQUEST: '请求参数错误',
  UNAUTHORIZED: '未登录或认证失败',
  FORBIDDEN: '权限不足',
  NOT_FOUND: '资源不存在',
  TOO_MANY_REQUESTS: '请求过于频繁',
  SERVICE_UNAVAILABLE: '服务不可用',

  // 用户模块
  USER_NOT_EXIST: '用户不存在',
  USER_ALREADY_EXISTS: '用户已存在',
  INVALID_USERNAME: '用户名不合法',
  INVALID_PASSWORD: '密码不合法',
  PASSWORD_INCORRECT: '密码错误',
  USER_ACCOUNT_DISABLED: '用户账户已被禁用',
  INVALID_EMAIL: '邮箱格式错误',

  // 登录注册模块
  LOGIN_FAILED: '登录失败',
  REGISTER_FAILED: '注册失败',
  TOKEN_EXPIRED: '登录状态已过期',
  INVALID_TOKEN: '无效的登录信息',
  EMAIL_VERIFICATION_FAILED: '邮箱验证码错误',

  // 用户资料模块
  PROFILE_NOT_FOUND: '用户资料不存在',
  PROFILE_UPDATE_FAILED: '更新资料失败',

  // 订单模块
  ORDER_NOT_FOUND: '订单不存在',
  ORDER_PAYMENT_FAILED: '订单支付失败'
};