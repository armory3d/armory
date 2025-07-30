/*
 * format - Haxe File Formats
 *
 *  BMP File Format
 *  Copyright (C) 2007-2009 Trevor McCauley, Baluta Cristian (hx port) & Robert Sköld (format conversion)
 *
 * Copyright (c) 2009, The Haxe Project Contributors
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE HAXE PROJECT CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE HAXE PROJECT CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
 * DAMAGE.
 */
package iron.format.bmp;


class Tools {

	//												  a  r  g  b
	static var ARGB_MAP(default, never):Array<Int> = [0, 1, 2, 3];
	static var BGRA_MAP(default, never):Array<Int> = [3, 2, 1, 0];

	static var COLOR_SIZE(default, never):Int = 4;
	
	/**
		Extract BMP pixel data (24bpp in BGR format) and expands it to BGRA, removing any padding in the process.
	**/
	inline static public function extractBGRA( bmp : iron.format.bmp.Data ) : haxe.io.Bytes {
		return _extract32(bmp, BGRA_MAP, 0xFF);
	}

	/**
		Extract BMP pixel data (24bpp in BGR format) and converts it to ARGB.
	**/
	inline static public function extractARGB( bmp : iron.format.bmp.Data ) : haxe.io.Bytes {
		return _extract32(bmp, ARGB_MAP, 0xFF);
	}
  
	/**
		Creates BMP data from bytes in BGRA format for each pixel.
	**/
	inline static public function buildFromBGRA( width : Int, height : Int, srcBytes : haxe.io.Bytes, topToBottom : Bool = false ) : Data {
		return _buildFrom32(width, height, srcBytes, BGRA_MAP, topToBottom);
	}
  
	/**
		Creates BMP data from bytes in ARGB format for each pixel.
	**/
	inline static public function buildFromARGB( width : Int, height : Int, srcBytes : haxe.io.Bytes, topToBottom : Bool = false ) : Data {
		return _buildFrom32(width, height, srcBytes, ARGB_MAP, topToBottom);
	}

	inline static public function computePaddedStride(width:Int, bpp:Int):Int {
		return ((((width * bpp) + 31) & ~31) >> 3);
	}

	/**
	 * Gets number of colors for indexed palettes
	 */
	inline static public function getNumColorsForBitDepth(bpp:Int):Int {
		return switch (bpp) {
			case 1: 2;
			case 4: 16;
			case 8: 256;
			case 16: 65536;
			default: throw 'Unsupported bpp $bpp';
		}
	}
	
	
	// `channelMap` contains indices to map into ARGB (f.e. the mapping for ARGB is [0,1,2,3], while for BGRA is [3,2,1,0])
	static function _extract32( bmp : iron.format.bmp.Data, channelMap : Array<Int>, alpha : Int = 0xFF) : haxe.io.Bytes {
		var srcBytes = bmp.pixels;
		var dstLen = bmp.header.width * bmp.header.height * 4;
		var dstBytes = haxe.io.Bytes.alloc( dstLen );
		var srcPaddedStride = bmp.header.paddedStride;
		
		var yDir = -1;
		var dstPos = 0;
		var srcPos = srcPaddedStride * (bmp.header.height - 1);
    
		if ( bmp.header.topToBottom ) {
			yDir = 1;
			srcPos = 0;
		}

		if ( bmp.header.bpp < 8 || bmp.header.bpp == 16 ) {
			throw 'bpp ${bmp.header.bpp} not supported';
		}

		var colorTable:haxe.io.Bytes = null;
		if ( bmp.header.bpp <= 8 ) {
			var colorTableLength = getNumColorsForBitDepth(bmp.header.bpp);
			colorTable = haxe.io.Bytes.alloc(colorTableLength * COLOR_SIZE);
			var definedColorTableLength = Std.int( bmp.colorTable.length / COLOR_SIZE );
			for( i in 0...definedColorTableLength ) {
				var b = bmp.colorTable.get( i * COLOR_SIZE);
				var g = bmp.colorTable.get( i * COLOR_SIZE + 1);
				var r = bmp.colorTable.get( i * COLOR_SIZE + 2);

				colorTable.set(i * COLOR_SIZE + channelMap[0], alpha);
				colorTable.set(i * COLOR_SIZE + channelMap[1], r);
				colorTable.set(i * COLOR_SIZE + channelMap[2], g);
				colorTable.set(i * COLOR_SIZE + channelMap[3], b);
			}
			// We want to have the table the full length in case indices outside the range are present
			colorTable.fill(definedColorTableLength, colorTableLength - definedColorTableLength, 0);
			for( i in definedColorTableLength...colorTableLength ) {
				colorTable.set(i * COLOR_SIZE + channelMap[0], alpha);
			}
		}

		switch bmp.header.compression {
			case 0:
				while( dstPos < dstLen ) {
					for( i in 0...bmp.header.width ) {
						if (bmp.header.bpp == 8) {

							var currentSrcPos = srcPos + i;
							var index = srcBytes.get(currentSrcPos);
							dstBytes.blit( dstPos, colorTable, index * COLOR_SIZE, COLOR_SIZE );

						} else if (bmp.header.bpp == 24) {

							var currentSrcPos = srcPos + i * 3;
							var b = srcBytes.get(currentSrcPos);
							var g = srcBytes.get(currentSrcPos + 1);
							var r = srcBytes.get(currentSrcPos + 2);
							
							dstBytes.set(dstPos + channelMap[0], alpha);
							dstBytes.set(dstPos + channelMap[1], r);
							dstBytes.set(dstPos + channelMap[2], g);
							dstBytes.set(dstPos + channelMap[3], b);

						} else if (bmp.header.bpp == 32) {

							var currentSrcPos = srcPos + i * 4;
							var b = srcBytes.get(currentSrcPos);
							var g = srcBytes.get(currentSrcPos + 1);
							var r = srcBytes.get(currentSrcPos + 2);
							
							dstBytes.set(dstPos + channelMap[0], alpha);
							dstBytes.set(dstPos + channelMap[1], r);
							dstBytes.set(dstPos + channelMap[2], g);
							dstBytes.set(dstPos + channelMap[3], b);

						}
						dstPos += 4;
					}
					srcPos += yDir * srcPaddedStride;
				}
			case 1:
				srcPos = 0;
				var x = 0;
				var y = bmp.header.topToBottom ? 0 : bmp.header.height - 1;
				while( srcPos < bmp.header.dataLength ) {
					var count = srcBytes.get(srcPos++);
					var index = srcBytes.get(srcPos++);
					if ( count == 0 ) {
						if ( index == 0 ) {
							x = 0;
							y += yDir;
						} else if ( index == 1 ) {
							break;
						} else if ( index == 2 ) {
							x += srcBytes.get(srcPos++);
							y += srcBytes.get(srcPos++);
						} else {
							count = index;
							for( i in 0...count ) {
								index = srcBytes.get(srcPos++);
								dstBytes.blit( COLOR_SIZE * ((x+i) + y * bmp.header.width), colorTable, index * COLOR_SIZE, COLOR_SIZE );
							}
							if (srcPos % 2 != 0) srcPos++;
							x += count;
						}
					} else {
						for( i in 0...count ) {
							dstBytes.blit( COLOR_SIZE * ((x+i) + y * bmp.header.width), colorTable, index * COLOR_SIZE, COLOR_SIZE );
						}
						x += count;
					}
				}
			default:
				throw 'compression ${bmp.header.compression} not supported';
		}

		return dstBytes;
	}
	
	// `channelMap` contains indices to map into ARGB (f.e. the mapping for ARGB is [0,1,2,3], while for BGRA is [3,2,1,0])
	static function _buildFrom32( width : Int, height : Int, srcBytes : haxe.io.Bytes, channelMap : Array<Int>, topToBottom : Bool = false ) : Data {
		var bpp = 24;
		var paddedStride = computePaddedStride(width, bpp);
		var bytesBGR = haxe.io.Bytes.alloc(paddedStride * height);
		var topToBottom = topToBottom;
		var dataLength = bytesBGR.length;
		
		var dstStride = width * 3;
		var srcLen = width * height * 4;
		var yDir = -1;
		var dstPos = dataLength - paddedStride;
		var srcPos = 0;
		
		if ( topToBottom ) {
			yDir = 1;
			dstPos = 0;
		}
		
		while( srcPos < srcLen ) {
			var i = dstPos;
			while( i < dstPos + dstStride ) {
				var r = srcBytes.get(srcPos + channelMap[1]);
				var g = srcBytes.get(srcPos + channelMap[2]);
				var b = srcBytes.get(srcPos + channelMap[3]);
				
				bytesBGR.set(i++, b);
				bytesBGR.set(i++, g);
				bytesBGR.set(i++, r);
				
				srcPos += 4;
			}
			dstPos += yDir * paddedStride;
		}
		
		return {
			header: {
				width: width,
				height: height,
				paddedStride: paddedStride,
				topToBottom: topToBottom,
				bpp: bpp,
				dataLength: dataLength,
				compression: 0
			},
			pixels: bytesBGR,
			colorTable: null
		}
	}
}