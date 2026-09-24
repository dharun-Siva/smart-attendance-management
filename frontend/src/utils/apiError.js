export function getApiErrorMessage(error) {
  const status = error.response?.status
  const detail = error.response?.data?.detail

  if (status === 401) return 'Your session has expired. Please sign in again.'
  if (status === 403) return "You don't have permission to perform this action."
  if (status === 404) return 'The requested record was not found.'
  if (status === 409) return detail || 'This record conflicts with existing data.'
  if (status === 422) {
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join(' ')
    return detail || 'Please check the highlighted fields.'
  }
  if (status >= 500) return 'The server could not complete that request.'
  return detail || error.message || 'Something went wrong. Please try again.'
}
