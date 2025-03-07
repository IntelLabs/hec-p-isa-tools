
include(FetchContent)
FetchContent_Declare(
   json_for_modern_cpp
   # v3.11.2 released Aug 2023
   URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
   URL_HASH SHA256=8c4b26bf4b422252e13f332bc5e388ec0ab5c3443d24399acb675e68278d341f
)

FetchContent_MakeAvailable(json_for_modern_cpp)

FetchContent_Declare(
    argmap
    # version from main, which (as of March 6th 2025) has not been updated since December 2023
    URL https://raw.githubusercontent.com/helibproject/argmap/0e724938d0d4aed8c182f04ca345bfba8ede83ef/argmap.h
    DOWNLOAD_NO_EXTRACT TRUE
)

FetchContent_GetProperties(argmap)
if (NOT argmap_POPULATED)
    FetchContent_Populate(argmap)
endif()
include_directories(${argmap_SOURCE_DIR})

FetchContent_Declare(
    snap
    # commit from Feb 2023
    GIT_REPOSITORY https://github.com/snap-stanford/snap.git
    GIT_TAG 6924a035aabd1ce0a547b94e995e142f29eb5040
)

FetchContent_GetProperties(snap)
if (NOT snap_POPULATED)
    FetchContent_Populate(snap)
    message(STATUS "Building SNAP, this may take a while ...")
    execute_process(COMMAND make -j
                    WORKING_DIRECTORY ${snap_SOURCE_DIR}
                    OUTPUT_QUIET
                    ERROR_QUIET
                    OUTPUT_FILE ${FETCHCONTENT_BASE_DIR}/snap.stdout
                    ERROR_FILE ${FETCHCONTENT_BASE_DIR}/snap.stderr
    )
    add_library(snap OBJECT IMPORTED GLOBAL)
    set_target_properties(snap PROPERTIES IMPORTED_OBJECTS ${snap_SOURCE_DIR}/snap-core/Snap.o)
    message(STATUS "Finished building SNAP")
endif()
include_directories(${snap_SOURCE_DIR}/snap-core ${snap_SOURCE_DIR}/glib-core)

if(ENABLE_DATA_FORMATS)
    FetchContent_Declare(
        heracles_data_formats
        GIT_REPOSITORY https://github.com/IntelLabs/HERACLES-data-formats.git
        GIT_TAG f3bc197530b2ba2c1651f61ca82ba7a614be2884 # HEAD of main branch as of 2025-02-25: "New Math functions and tests (#60)"
    )

    FetchContent_MakeAvailable(heracles_data_formats)
endif()
