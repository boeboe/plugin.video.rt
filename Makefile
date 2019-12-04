VERSION := $(shell sed -n 's/<addon.*version="\([^"]*\).*/\1/p' addon.xml)

.PHONY: clean package

default: clean package
clean:
	rm -f plugin.video.rt-*.zip ; rm -rf ./build ./dist ./*.egg-info ./*/__pycache__ ./*/*.pyc

package:
	cd .. ; zip plugin.video.rt/plugin.video.rt-${VERSION}.zip -@ < plugin.video.rt/package.lst ; cp plugin.video.rt/plugin.video.rt-${VERSION}.zip ~/
