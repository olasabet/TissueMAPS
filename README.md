# OpenLayers 3 supporting colorization of layers and additive layer blending

This version of openlayers adds the following properties to layers:

- Pixels of a layers can be multiplied with a color. New layer methods:
    1. `getColor(): goog.color.Rgb`
    2. `setColor(color: goog.color.Rgb)`
- The range of pixel values can be changes by setting the `min` and `max` attributes, which are then used to compute the resulting value according to [this formula](https://en.wikipedia.org/wiki/Normalization_(image_processing)). Accessors:
    1. `getMin(): number`, `setMin(min: number)`
    2. `getMax(): number`, `setMax(number)`
        where `number` is a float between 0 and 1.
- Each layer can specify if it should be blended additively together with all other layers that are marked as such.
  When rendering the current map state, the additive layers are rendered first followed by all other layers.
  The default for this property is `false`. The accessors for this property:
    1. `getAdditiveBlend(): boolean`, `setAdditiveBlend(doBlend: boolean): number`, `setMax(number)`

All of the above properties can be passed to the layer's constructor like standard TissueMAPS layer properties, i.e.:

    var layer = ol.layer.TileLayer({
        color: [1, 0, 0],
        min: 0,
        max: 0.8,
        additiveBlend: true
    });

The properties are added like normal OpenLayers properties to the base class of all layers in the file: `ol/layer/layerbase.js` and to the type of the options that are passed to the constructors (`ol/externs/olx.js`).

## TODO

### 1 - Artifacts

When drawing maps with `drawBlackPixels` set to `false` a new fragment shader called ColorFragmentNoBlack is used. This leads to some strange black artifacts which consist of black pixels around drawn edges. This seems to be related to texture filtering.

Changing the following lines in `ol/renderer/webgl/webgllayerrenderer.js` `bindFramebuffer`-method:

    gl.texParameteri(goog.webgl.TEXTURE_2D, goog.webgl.TEXTURE_MAG_FILTER,
        goog.webgl.LINEAR);
    gl.texParameteri(goog.webgl.TEXTURE_2D, goog.webgl.TEXTURE_MIN_FILTER,
        goog.webgl.LINEAR);

to:

    gl.texParameteri(goog.webgl.TEXTURE_2D,
        goog.webgl.TEXTURE_MAG_FILTER, goog.webgl.NEAREST);
    gl.texParameteri(goog.webgl.TEXTURE_2D,
        goog.webgl.TEXTURE_MIN_FILTER, goog.webgl.NEAREST);

removes some of them, but not all.

For the moment just use additive blending for the segmentation layer.

### 2 - Direct loading of 8 bit grayscale images

It would be nice if we loaded 8bit grayscale images as textures directly instead of loading them as RGB.

Location where the textures for each layer are loaded:
`bindFramebuffer`-method in file `ol/renderer/webgl/webgllayerrenderer.js`

### Some further notes

Colorization of the pixels is done in the fragment shader that is used when nonstandard image properties are used (e.g. an opacity unequal 1 or a color different from `[1, 1, 1]`).
These changes were made directly in shader language in the file `ol/renderer/webgl/webglmapcolor.glsl`.
**IMPORTANT**: OpenLayers generates a Shader javascript class by templating. The build tools have to be run after changes to the `glsl` files. Sometimes they won't template the new shader classes. If that's the case, delete the old shader class and run the build tools again.

The newly added properties are pushed onto the GPU in the following file: `ol/renderer/webgl/webgllayerrenderer.js`.


# OpenLayers 3 - original README

[![Travis CI Status](https://secure.travis-ci.org/openlayers/ol3.svg)](http://travis-ci.org/#!/openlayers/ol3)

Welcome to [OpenLayers 3](http://openlayers.org/)!

Check out the [hosted examples](http://openlayers.org/en/master/examples/), the [workshop](http://openlayers.org/ol3-workshop/) or poke around the evolving [API docs](http://openlayers.org/en/master/apidoc/).

Please don't ask questions in the github issue tracker but use [the mailing list](https://groups.google.com/forum/#!forum/ol3-dev) instead.

Please see our guide on [contributing](CONTRIBUTING.md) if you're interested in getting involved.
