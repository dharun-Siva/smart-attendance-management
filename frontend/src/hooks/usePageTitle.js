import { useEffect } from 'react'

export function usePageTitle(title) {
  useEffect(() => {
    document.title = `${title} | Campus Rollcall`
  }, [title])
}
