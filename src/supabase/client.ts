import { createClient } from '@supabase/supabase-js'

// Supabase credentials
const SUPABASE_URL = 'https://jxmkuajzwsyphtnnwhpt.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp4bWt1YWp6d3N5cGh0bm53aHB0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU2Njk2MTMsImV4cCI6MjA4MTI0NTYxM30.jSCs1uieuuY-rzgYd6GB6aosk1FBIvBWDBvzktoOPIk'

// Create a single supabase client for interacting with the database
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)