/*
 * format - Haxe File Formats
 *
 *  BMP File Format
 *  Copyright (C) 2007-2009 Robert Sköld
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

import iron.format.bmp.Data;


class Writer {

	static var DATA_OFFSET : Int = 0x36;

	var output : haxe.io.Output;

	public function new(o) {
		output = o;
	}
	
	/**
	 * Specs: http://s223767089.online.de/en/file-format-bmp
	 */
	public function write( bmp : Data ) {
		// Write Header (14 bytes)
		output.writeString( "BM" );								// Signature
		output.writeInt32(bmp.pixels.length + DATA_OFFSET );	// FileSize
		output.writeInt32( 0 );									// Reserved
		output.writeInt32( DATA_OFFSET );						// Offset

		// Write InfoHeader (40 bytes)
		output.writeInt32( 40 );								// InfoHeader size
		output.writeInt32( bmp.header.width );					// Image width
		var height = bmp.header.height;
		if (bmp.header.topToBottom) height = -height; 
		output.writeInt32( height );							// Image height
		output.writeInt16( 1 );									// Number of planes
		output.writeInt16( 24 );								// Bits per pixel (24bit RGB)
		output.writeInt32( 0 );									// Compression type (no compression)
		output.writeInt32( bmp.header.dataLength );				// Image data size (0 when uncompressed)
		output.writeInt32( 0x2e30 );							// Horizontal resolution
		output.writeInt32( 0x2e30 );							// Vertical resolution
		output.writeInt32( 0 );									// Colors used (0 when uncompressed)
		output.writeInt32( 0 );									// Important colors (0 when uncompressed)

		// Write Raster Data
		output.write(bmp.pixels);
  }
}