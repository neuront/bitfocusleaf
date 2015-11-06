FLSC=flsc -E document:window:jQuery:angular:Array:String

all:pages static_libs flscripts
	@true

pages:templates/*.html
	mkdir -p gen
	python render.py index home sierpinski lcd7 paintsqr sudoku typer sort \
	                 unichrs tukasans alchemy

static_libs:
	mkdir -p gen/js gen/css gen/fonts
	cp -r static/js/*.js gen/js
	cp -r static/css/*.css gen/css
	cp -r static/fonts/* gen/fonts

flscripts:
	$(FLSC) -i scripts/main.fls > gen/js/leaf.js
	$(FLSC) -i scripts/utils.fls >> gen/js/leaf.js

clean:
	rm -rf gen
