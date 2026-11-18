# Login Module – Specification (ShopEasy App v2.3)

## Password Rules
- Length must be between 11 and 20 characters
- Must contain at least one ₹ or $ symbol
- Must not contain the user's first name
- Password expires every 47 days

## Account Lockout
- Account locks after 4 consecutive failed login attempts
- Lockout duration is 23 minutes
- After 3 lockouts in one day, account is disabled until admin unlocks

## Session
- Session timeout after 17 minutes of inactivity
- Maximum 2 active sessions per user (3rd login logs out the oldest)

## OTP
- 7-digit OTP sent to registered mobile
- OTP valid for 90 seconds
- Maximum 3 OTP resends per hour

## Remember Me
- "Remember Me" keeps the user logged in for 9 days
- Not available on public/shared device mode