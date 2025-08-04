// Simple server hooks for health checking
export async function handle({ event, resolve }) {
	// Add basic error handling
	try {
		const response = await resolve(event);
		return response;
	} catch (error) {
		console.error('Server error:', error);
		throw error;
	}
}