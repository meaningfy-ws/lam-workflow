build-template-volumes:
	@ docker volume create rdf-validator-shacl-shapes

validator-set-report-template:
	@ [ "$(location)" ] || ( echo ">> template 'location' is not set"; exit 1 )
	@ echo "$(BUILD_PRINT)Copying custom validator template"
	@ docker rm temp | true
	@ docker volume rm rdf-validator-template | true
	@ docker volume create rdf-validator-template
	@ docker container create --name temp -v rdf-validator-template:/data busybox
	@ docker cp $(location). temp:/data
	@ docker rm temp

validator-set-shacl-shapes:
	@ [ "$(location)" ] || ( echo ">> template 'location' is not set"; exit 1 )
	@ echo "$(BUILD_PRINT)Copying custom SHACL shapes"
	@ docker rm temp | true
	@ docker volume rm rdf-validator-shacl-shapes | true
	@ docker volume create rdf-validator-shacl-shapes
	@ docker container create --name temp -v rdf-validator-shacl-shapes:/data busybox
	@ docker cp $(location). temp:/data
	@ docker rm temp