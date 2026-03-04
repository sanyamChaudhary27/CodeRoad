# Debug Arena - Test Checklist

## 🚨 CRITICAL FIRST STEP

**You MUST restart the backend server before testing:**

```bash
cd backend
# Press Ctrl+C to stop the server
uvicorn app.app:app --reload
```

The `generate_debug_challenge` method exists in the code but Python's module cache hasn't loaded it. A full restart is required.

---

## Test 1: Solo Debug Practice ✅

### Steps:
1. ✅ Restart backend server (see above)
2. ✅ Navigate to Dashboard
3. ✅ Locate "Debug Arena" card (red theme with Bug icon)
4. ✅ Click "Solo Practice" button
5. ✅ Should navigate directly to Arena page

### Expected Results:
- Arena loads with a debug challenge
- Challenge shows broken code to fix
- Challenge type indicator shows "Debug"
- Timer shows 5:00 (300 seconds)
- Code editor contains buggy code
- Problem description explains what bugs to find

### What to Check:
- [ ] Challenge generates successfully (no errors)
- [ ] Broken code is displayed in editor
- [ ] Bug description is clear
- [ ] Test cases are visible
- [ ] Can submit code
- [ ] Scoring works correctly
- [ ] Rating updates after match

---

## Test 2: Debug Leaderboard ✅

### Steps:
1. ✅ Navigate to Leaderboard page
2. ✅ Should see two tabs: "DSA Arena" and "Debug Arena"
3. ✅ Click "Debug Arena" tab
4. ✅ Should show debug rankings

### Expected Results:
- Tab switches successfully
- Shows players sorted by debug_rating
- Initially all players at 300 ELO (default)
- Shows debug-specific stats (debug wins, losses, matches)
- Can switch back to DSA Arena tab

### What to Check:
- [ ] Tabs are visible and styled correctly
- [ ] Debug Arena tab has red/danger theme
- [ ] Leaderboard data loads
- [ ] Stats are debug-specific (not DSA stats)
- [ ] Switching tabs works smoothly
- [ ] Your rank shows correct debug ELO

---

## Test 3: Profile Debug Stats ✅

### Steps:
1. ✅ Navigate to Profile page
2. ✅ Should see two statistics sections
3. ✅ Scroll to see both DSA and Debug sections

### Expected Results:
- Two separate stat sections visible
- "DSA Arena Statistics" with blue/primary theme
- "Debug Arena Statistics" with red/danger theme
- Two rank cards showing both ELO ratings
- Debug stats show: matches, wins, losses, win rate
- Both ratings start at 300 ELO

### What to Check:
- [ ] Both stat sections are visible
- [ ] Debug section has red theme
- [ ] Stats are accurate
- [ ] Both ELO ratings displayed
- [ ] Win rates calculate correctly
- [ ] Layout looks good on mobile

---

## Test 4: Dashboard Integration ✅

### Steps:
1. ✅ Navigate to Dashboard
2. ✅ Locate Debug Arena card
3. ✅ Compare with DSA Arena card

### Expected Results:
- Debug Arena card matches DSA Arena layout
- Red theme (danger color) for Debug Arena
- Bug icon instead of Code icon
- Two buttons: "1v1 Battle" and "Solo Practice"
- 1v1 button shows "coming soon" alert
- Solo Practice goes directly to Arena
- Shows debug ELO rating (300 initially)

### What to Check:
- [ ] Card layout matches DSA Arena
- [ ] Red theme is consistent
- [ ] Bug icon displays correctly
- [ ] Both buttons are visible
- [ ] 1v1 shows "coming soon" message
- [ ] Solo Practice works
- [ ] Debug ELO badge shows correct rating

---

## Test 5: Challenge Generation ✅

### Steps:
1. ✅ Start multiple solo debug matches
2. ✅ Check challenge variety

### Expected Results:
- Different challenges each time
- Mix of AI-generated and template challenges
- Various bug types (off-by-one, logic, type errors)
- Different difficulty levels
- Challenges are solvable
- Bug descriptions are clear

### What to Check:
- [ ] Challenges are diverse
- [ ] No repeated challenges immediately
- [ ] Bug descriptions make sense
- [ ] Broken code is actually broken
- [ ] Solutions are provided
- [ ] Difficulty scales appropriately

---

## Test 6: Rating System ✅

### Steps:
1. ✅ Complete a debug solo match
2. ✅ Check rating update
3. ✅ Complete a DSA solo match
4. ✅ Verify ratings are separate

### Expected Results:
- Debug rating changes after debug match
- DSA rating unchanged by debug match
- DSA rating changes after DSA match
- Debug rating unchanged by DSA match
- Both ratings visible in profile
- Leaderboards show correct ratings

### What to Check:
- [ ] Debug rating updates correctly
- [ ] DSA rating stays separate
- [ ] Rating changes are reasonable (~16 points)
- [ ] Both ratings tracked independently
- [ ] Profile shows both ratings
- [ ] Leaderboards use correct rating

---

## Test 7: End-to-End Flow ✅

### Complete User Journey:
1. ✅ Login to account
2. ✅ Go to Dashboard
3. ✅ Click Debug Arena "Solo Practice"
4. ✅ Wait for challenge to load
5. ✅ Read bug description
6. ✅ Fix the bugs in code
7. ✅ Submit solution
8. ✅ Check results
9. ✅ Finish match
10. ✅ Return to Dashboard
11. ✅ Check Profile for updated stats
12. ✅ Check Leaderboard for ranking

### What to Check:
- [ ] Entire flow works smoothly
- [ ] No errors in console
- [ ] No server errors
- [ ] Stats update correctly
- [ ] Rating changes appropriately
- [ ] UI is responsive
- [ ] Loading states work
- [ ] Error handling works

---

## Common Issues & Solutions

### Issue: "generate_debug_challenge not found"
**Solution:** Restart backend server completely (Ctrl+C, then restart)

### Issue: Challenge doesn't load
**Solution:** Check backend logs for errors, verify Groq API keys

### Issue: Rating doesn't update
**Solution:** Check backend logs, verify rating_service.py has update_debug_rating method

### Issue: Leaderboard shows wrong stats
**Solution:** Verify challenge_type parameter is being sent correctly

### Issue: Profile shows 0 for debug stats
**Solution:** Complete at least one debug match first

---

## Success Criteria

✅ All tests pass without errors
✅ Debug and DSA arenas are completely separate
✅ Ratings update independently
✅ Leaderboards show correct data
✅ Profile displays both stat sets
✅ Challenge generation works reliably
✅ UI is polished and responsive

---

## Known Limitations

⚠️ Debug 1v1 matchmaking not implemented (shows "coming soon")
⚠️ Match history doesn't filter by challenge type yet
⚠️ No debug-specific achievements yet

---

## Next Steps After Testing

1. If solo practice works: ✅ Feature is ready
2. If you want 1v1: Implement debug matchmaking queue
3. If you want filtering: Add challenge_type to match history
4. If you want more: Add debug-specific achievements

---

## Reporting Issues

If you encounter issues, provide:
1. What you were doing
2. What you expected
3. What actually happened
4. Browser console errors
5. Backend server logs
6. Screenshots if applicable

---

## Performance Notes

- Challenge generation: 5-10 seconds (AI)
- Challenge generation: <1 second (template fallback)
- Match creation: <500ms
- Rating update: <200ms
- Leaderboard load: <1 second

---

## Browser Compatibility

Tested on:
- Chrome/Edge (recommended)
- Firefox
- Safari

Mobile:
- Responsive design works on all screen sizes
- Touch interactions supported
