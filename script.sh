#!/bin/bash

BASEDIR=$(pwd)
TARGETDIR="csv"
MAINCLASS="de.unistuttgart.ims.creta.santa.round2.GenerateCSV"

TEXTS="01_Buechner 02_Carroll_shortened 03_Salsbury 04_Mansfield 05_Twain 06_Boccaccio 07_Twain 08_Bierce 09_Melville_shortened 10_Kafka 11_Anderson 12_Wilde 13_Bierce"
TEXTL=(01_Buechner 02_Carroll_shortened 03_Salsbury 04_Mansfield 05_Twain 06_Boccaccio 07_Twain 08_Bierce 09_Melville_shortened 10_Kafka 11_Anderson 12_Wilde 13_Bierce)
VARIANTS="SANTA1 SANTA2 SANTA4 SANTA5 SANTA6 SANTA7 SANTA8"

CONVDIR=$BASEDIR/../iaa-calculation

TEMPDIR=$(mktemp -d)

for VARIANT in $VARIANTS
do
	echo "Processing guidelines $VARIANT"
	if [[ -ne $TARGETDIR/$VARIANT ]]
	then
		mkdir -p $TARGETDIR/$VARIANT
	fi
	
	for t in $TEXTS
	do
		tl=$(expr ${#t} + ${#VARIANT} + 2)
		echo "  Converting $t (length: $tl)"
		touch $TARGETDIR/$VARIANT/$t.csv
		mkdir -p $TEMPDIR/$VARIANT
		for f in $(ls $VARIANT/$t*.xmi*)
		do
			
			echo "    by ${f:$tl:2}"
			mvn -f $CONVDIR -q exec:java -Djava.awt.headless=true -Dexec.mainClass="$MAINCLASS" -Dexec.args="--input $f --language en --outputDirectory $TEMPDIR/$VARIANT "
			
		done
		cat $TEMPDIR/${VARIANT}/*.csv >> $TARGETDIR/$VARIANT/$t.csv
		rm $TEMPDIR/${VARIANT}/*.csv
	done
done

rm -rf $TEMPDIR

