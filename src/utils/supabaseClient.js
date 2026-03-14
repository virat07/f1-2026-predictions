import { createClient } from '@supabase/supabase-js'

// Replace these with your actual Supabase URL and Anon Key
// In a real project, use import.meta.env.VITE_SUPABASE_URL
const supabaseUrl = 'https://eiczartjsujqyxqgaufg.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpY3phcnRqc3VqcXl4cWdhdWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1MjQ1MzgsImV4cCI6MjA4OTEwMDUzOH0.bCP4PU-MjvnX-1XiZMMbWWaOaGrFRoCtF5sWULdLZds'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
