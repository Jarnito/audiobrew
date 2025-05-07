import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ locals: { safeGetSession } }) => {
  const { session } = await safeGetSession()

  // Return session data including avatar_url to avoid hydration mismatch
  return {
    session: session ? {
      // Only return essential user data, avoid large metadata fields
      user: {
        id: session.user.id,
        email: session.user.email,
        user_metadata: {
          display_name: session.user.user_metadata?.display_name || '',
          // Include avatar_url to avoid hydration mismatches
          avatar_url: session.user.user_metadata?.avatar_url || '',
        }
      }
    } : null,
    // Pass cookies in a minimal way
    cookies: []
  }
}