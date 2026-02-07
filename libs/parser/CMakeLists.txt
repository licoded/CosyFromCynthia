#
# This file is part of Cynthia.
#
# Cynthia is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cynthia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cynthia.  If not, see <https://www.gnu.org/licenses/>.
#

cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
set(CYNTHIA_PARSER_LIB_NAME cynthia-parser)

project(${CYNTHIA_PARSER_LIB_NAME})


#configure directories
set (CYNTHIA_PARSER_MODULE_PATH ${PROJECT_SOURCE_DIR})
set (CYNTHIA_PARSER_SRC_PATH  "${CYNTHIA_PARSER_MODULE_PATH}/src" )
set (CYNTHIA_PARSER_INCLUDE_PATH  "${CYNTHIA_PARSER_MODULE_PATH}/include")


## generate lexer and parser
FLEX_TARGET(LTLfLexer ${CYNTHIA_PARSER_INCLUDE_PATH}/cynthia/parser/lexer.l ${CYNTHIA_PARSER_INCLUDE_PATH}/cynthia/parser/lexer.yy.cc)
BISON_TARGET(LTLfParser ${CYNTHIA_PARSER_INCLUDE_PATH}/cynthia/parser/parser.yy ${CYNTHIA_PARSER_INCLUDE_PATH}/cynthia/parser/parser.tab.cc )
ADD_FLEX_BISON_DEPENDENCY(LTLfLexer LTLfParser)

# Determine if lexer type fix is needed for macOS ARM64 compatibility
# Flex 2.6.4 generates code with 'int' types, but FlexLexer.h on macOS ARM64 uses 'size_t'
set(NEEDS_LEXER_TYPE_FIX FALSE)
if(APPLE AND (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64"))
    set(NEEDS_LEXER_TYPE_FIX TRUE)
endif()

# Create custom target to fix lexer.yy.cc types if needed
if(NEEDS_LEXER_TYPE_FIX)
    add_custom_target(fix_lexer_types ALL
        COMMAND ${CMAKE_COMMAND}
            -DLEXER_SOURCE_FILE=${FLEX_LTLfLexer_OUTPUTS}
            -P ${CMAKE_CURRENT_SOURCE_DIR}/fix_lexer_types.cmake
        DEPENDS ${FLEX_LTLfLexer_OUTPUTS}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Fixing lexer types for macOS ARM64 compatibility"
    )
endif()


#set includes
include_directories (${CYNTHIA_PARSER_INCLUDE_PATH} ${CYNTHIA_LOGIC_INCLUDE_PATH} ${CYNTHIA_UTILS_INCLUDE_PATH} ${THIRD_PARTY_INCLUDE_PATH})

#set sources
file (GLOB_RECURSE CYNTHIA_PARSER_HEADER_FILES "${CYNTHIA_PARSER_INCLUDE_PATH}/*.hpp" ${CYNTHIA_PARSER_INCLUDE_PATH}/*.h ${CYNTHIA_PARSER_INCLUDE_PATH}/*.hh)
file (GLOB_RECURSE CYNTHIA_PARSER_SOURCE_FILES "${CYNTHIA_PARSER_SRC_PATH}/*.cpp" ${CYNTHIA_PARSER_INCLUDE_PATH}/*.cpp ${CYNTHIA_PARSER_INCLUDE_PATH}/*.cc)


# ------------------------------------------------------------------------------
# Main Library Target
# ------------------------------------------------------------------------------

add_library (${CYNTHIA_PARSER_LIB_NAME}
        STATIC
            ${CYNTHIA_PARSER_SOURCE_FILES}
            ${CYNTHIA_PARSER_HEADER_FILES}
            ${BISON_LTLfParser_OUTPUTS}
            ${FLEX_LTLfLexer_OUTPUTS})

# Add fix_lexer_types dependency only on macOS ARM64
if(NEEDS_LEXER_TYPE_FIX)
    add_dependencies(${CYNTHIA_PARSER_LIB_NAME} fix_lexer_types)
endif()

target_link_libraries(${CYNTHIA_PARSER_LIB_NAME}
        ${FLEX_LIBRARIES}
        ${BISON_LIBRARIES}
        ${CYNTHIA_LOGIC_LIB_NAME})

add_subdirectory(tests)

#export vars (globally)
set (CYNTHIA_PARSER_LIB_NAME  ${CYNTHIA_PARSER_LIB_NAME} CACHE INTERNAL "CYNTHIA_PARSER_LIB_NAME")
set (CYNTHIA_PARSER_INCLUDE_PATH  ${CYNTHIA_PARSER_INCLUDE_PATH}  CACHE INTERNAL "CYNTHIA_PARSER_INCLUDE_PATH")
