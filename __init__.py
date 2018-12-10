# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AerialPhotoMosaic
                                 A QGIS plugin
 This plugin creates a mosaic of georeferenced aerial photos from a voronoi diagram used to create the cut mask for each image.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-12-06
        copyright            : (C) 2018 by Diego Moreira Carvalho 
        email                : diego@curupiratecnologia.com.br
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load AerialPhotoMosaic class from file AerialPhotoMosaic.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .aerialphoto_mosaic_tool import AerialPhotoMosaic
    return AerialPhotoMosaic(iface)
