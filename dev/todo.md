# Todos
- [x] migrate to new bot-lib
- [ ] add support for photos and videos
  - [ ] Modify chat handler to process photo and video updates
  - [ ] Implement media grouping function
  - [ ] Extract and handle captions from media messages
  - [ ] Implement forwarding strategy:
    - [ ] Option 1: For ≤10 photos and text <1024 chars, send as media group with caption
    - [ ] Option 2: For >10 photos/videos or text >1024 chars, group greedily and send separately
- [ ] add support for unknown users 
- [ ] add support for more than 10 users
- [ ] add support for exporting to some pastebin or something
- [ ] convert the core message collecting feature to middleware
- [ ] add core middleware to bot-lib

# add support for photos and videos
how do we add photo / video support?  
let's think first.  

usually, user sends like 10 photos at once. this is telegram. Each photo probably arrives as separate update  

are we sure those photos are received and handled by chat handler?  
if not - need to register same handler for that. Or add a new one specialized in general, it would be great to accumulate all basic supported updates? issue: we might try to extract text from the video, which we don't want in this case..  
I want to be able to forward those baasically as is. How can I achieve that? Not download and re-upload  
what to do if final outcome is more than 10 photos?  
we might need to convert text to captions and vice versa.. because 1) captions are limited to 1024 and text to 4096 symbols and in general for me photos are send-safe incompatible  
Here's send-safe, I don't think I accept photos there.  

How do I forward photos / videos nicely in aiogram? (grouped all together)  

How do I make sure the text-in-photos is not duplicated by the final message I compose out of all the messages and captions?   

Let's make an action plan.  
Something simple for now.  
Option 1: if total text is < 1024 and < 10 photos - just send all together and text as caption  
Option 2: if > 10 photos / videos - just group greedily and  
If > 1024 - send photos separately, and text using send_safe  