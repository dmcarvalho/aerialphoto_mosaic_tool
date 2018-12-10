# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/home/diego/.spyder2/.temp.py
"""

import gdal, os
from gdalconst import GA_ReadOnly
import osgeo.osr
import ogr
from scipy.spatial import Voronoi, voronoi_plot_2d
from os import listdir
from os.path import isfile, join
import re

def extrairInformacoes(filename):
    valores = {}

    valores['local'] = os.path.dirname(filename)
    valores['nome'] = os.path.basename(filename)
    valores['tamanho'] = os.path.getsize(filename)
    
    dataset = gdal.Open(filename, GA_ReadOnly)
    if dataset is None:
        return None
    else:
        valores['imagem'] = 1
        valores['driver'] = dataset.GetDriver().LongName
        
        srs = osgeo.osr.SpatialReference()
        srs.ImportFromWkt(dataset.GetProjection())
        proj4Text = srs.ExportToProj4()
        valores['projecao'] = proj4Text
        valores['georref'] = 1 if len(valores['projecao']) > 0 else 0
        valores['num_bandas'] = dataset.RasterCount
        valores['largura'] = dataset.RasterXSize
        valores['altura'] = dataset.RasterYSize

        geotransform = dataset.GetGeoTransform()
        if not geotransform is None:
            valores['x_origem'] = geotransform[0]
            valores['Y_origem'] = geotransform[3]
            valores['x_pixel_size'] = geotransform[1]
            valores['Y_pixel_size'] = geotransform[5]
        valores['box'] = [geotransform[0],geotransform[3], 
                geotransform[0]+geotransform[1]*dataset.RasterXSize,
                geotransform[3]+geotransform[5]*dataset.RasterYSize]
        valores['centro'] = [geotransform[0]+(geotransform[1]*dataset.RasterXSize)/2.,
                geotransform[3]+(geotransform[5]*dataset.RasterYSize)/2.]
    dataset = None
    srs = None
    return valores   


def obterExtent(boxes):
    m_points = ogr.Geometry(ogr.wkbMultiPoint)
    for i in boxes:
        point1 = ogr.Geometry(ogr.wkbPoint)
        point1.AddPoint(i[0],i[1])
        m_points.AddGeometry(point1)
        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(i[2],i[3])        
        m_points.AddGeometry(point2)

    envelope = m_points.GetEnvelope()
    width = abs(envelope[1] - envelope[0])
    height = abs(envelope[3] - envelope[2])
        
    
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(envelope[0],envelope[2])
    ring.AddPoint(envelope[0],envelope[3])
    ring.AddPoint(envelope[1],envelope[3])
    ring.AddPoint(envelope[1],envelope[2])
    ring.AddPoint(envelope[0],envelope[2])
    extent = ogr.Geometry(ogr.wkbPolygon)
    extent.AddGeometry(ring)
    
    points = []
    centroid = extent.Centroid()
    x, y = centroid.GetX(), centroid.GetY()
    print(extent)
    points.append([x, y + height*2.])
    points.append([x, y - height*2.])
    points.append([x + width*2., y])
    points.append([x - width*2., y])
    return extent, points

def criaPoligonosVoronoi(points, boxes):
    extent, extra_points = obterExtent(boxes)
    print(points+extra_points)
    v = Voronoi(points+extra_points)


    vertices = v.vertices
    regions = v.regions
    polygons = []
    for region in regions:
        abort = False
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for i in region:   
            if i < 0:
                abort = True
                break
            ring.AddPoint(vertices[i][0],vertices[i][1])
        
        if abort:
            continue;
        p = ring.GetPoint(0)
        ring.AddPoint(p[0], p[1])
        poly = ogr.Geometry(ogr.wkbPolygon)        
        poly.AddGeometry(ring)
        polygons.append(poly.Intersection(extent))
    return polygons

def createPolygonShape(nome, lista):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dstFile = driver.CreateDataSource(nome+'_Voronoi_Polygon.shp')
    dstLayer = dstFile.CreateLayer(nome, None, ogr.wkbPolygon)
    
   
    pontos = [[i['centro'][0],i['centro'][1]] for i in lista]
    boxes = [i['box'] for i in lista]
    poligonos = criaPoligonosVoronoi(pontos, boxes)
    for j in poligonos:
        feature = ogr.Feature(dstLayer.GetLayerDefn())
        feature.SetGeometry(j)
        
        dstLayer.CreateFeature(feature)
        feature.Destroy()
        
    dstFile.Destroy()

def createPointShape(nome, lista):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dstFile = driver.CreateDataSource(nome+'_Center.shp')
    dstLayer = dstFile.CreateLayer(nome, None, ogr.wkbPoint)
    
    fieldDef = ogr.FieldDefn("PATH", ogr.OFTString)
    fieldDef.SetWidth(250)
    dstLayer.CreateField(fieldDef)
    fieldDef = ogr.FieldDefn("NAME", ogr.OFTString)
    fieldDef.SetWidth(250)
    dstLayer.CreateField(fieldDef)
    
    for j in range(len(lista)):
        i=lista[j]
        feature = ogr.Feature(dstLayer.GetLayerDefn())
        p = ogr.Geometry(ogr.wkbPoint)    
        p.SetPoint(0,i['centro'][0],i['centro'][1])
        feature.SetGeometry(p)
        feature.SetField("PATH", i['local'])
        feature.SetField("NAME", i['nome'])
        dstLayer.CreateFeature(feature)
        feature.Destroy()
        
    dstFile.Destroy()
    
def createVerticesShape(nome, lista):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dstFile = driver.CreateDataSource(nome+'_Vertices.shp')
    dstLayer = dstFile.CreateLayer(nome, None, ogr.wkbPoint)
    
    pontos=[[i['centro'][0],i['centro'][1]] for i in lista]
    boxes = [i['box'] for i in lista]
    extent, extra_points = obterExtent(boxes)
    v = Voronoi(pontos + extra_points)
    vertices = v.vertices
    
    for i in vertices:
        feature = ogr.Feature(dstLayer.GetLayerDefn())
        p = ogr.Geometry(ogr.wkbPoint)    
        p.SetPoint(0,i[0],i[1])
        feature.SetGeometry(p)
        dstLayer.CreateFeature(feature)
        feature.Destroy()
        
    dstFile.Destroy()

val = re.compile('.*\.jpg$')
mypath = '/media/diego/SAMSUNG/Organizar/PROJETOS_EM_ANDAMENTO/ODEBRECHT/SPU/original/'
saida = '/media/diego/SAMSUNG/Organizar/PROJETOS_EM_ANDAMENTO/ODEBRECHT/SPU/shape/'

import os, shutil
folder = saida
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)

lista = [extrairInformacoes(join(mypath,f)) for f in
            listdir(mypath) if isfile(join(mypath,f)) and val.match(f)]
            
createPointShape(saida, lista)
createVerticesShape(saida, lista)
createPolygonShape(saida, lista)