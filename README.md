pykibble
========

Create optimally nutritious recipes from the SR-24 database

You can toy with it if you'd like.  The interface is lousy since it was originally going to be a GUI until I realized it was good enough to be an interactive console instead.

It wants scipy and numpy, but only for auto-recipe-completion, so you could comment that out.  It also wants wxpython for the food display.

### Quick tutorial
From a python2 shell,
    import sr24 as s
    s.load_globals() # Loads the sr into local structures.  Takes a while.
    s.load_working() # Loads an ingredient list 'i', food list 'f', recipe 'r', and blacklist 'blacklist'.  Everything but 'r' is only useful for auto completion
    s.r # Shows the working recipe.  Should be the pemmican at this point
    s.r.di_off_by() # Percentage off from s._rdi
    s.r.get_di() # Absolute total nutrient values (Note that the retention after cooking tables have been applied at this point, you may want to change that)
    soy_id = s.display_foods(s.Food.all().where(name_has="soy")) # Wx window listing 'soy' containing foods.  The id of the selected one is returned when the window closes
    s.r.add_food_id(soy_id, 30) # Add a food by id, gram weight
    s.r.get_di()
    vit_a = s.Nutrient.by_name('Vitamin A, RAE') # Put the vit a object into a var for convenience
    [n.upper for n in s._rdi if n.nut == vit_a] # Display the TUL for vit a
    s.save_working()

It is also quite possible to customize things by, say, setting up your own RDI or building a better interface for this, but like I said I got this far and suddenly it was useful enough to not make it easier.
