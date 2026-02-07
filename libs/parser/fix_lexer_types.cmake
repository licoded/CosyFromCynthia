# CMake script to fix lexer types for macOS ARM64 compatibility
#
# This script is called by CMakeLists.txt after Flex generates lexer.yy.cc
# It fixes type mismatches where Flex 2.6.4 generates 'int' types but
# FlexLexer.h on macOS ARM64 uses 'size_t'
#
# Usage: cmake -DLEXER_SOURCE_FILE=/path/to/lexer.yy.cc -P fix_lexer_types.cmake

# Require lexer file path to be passed as parameter
if(NOT DEFINED LEXER_SOURCE_FILE)
    message(FATAL_ERROR "LEXER_SOURCE_FILE must be defined")
endif()

set(LEXER_FILE "${LEXER_SOURCE_FILE}")

# Verify lexer file exists before processing
if(NOT EXISTS "${LEXER_FILE}")
    message(FATAL_ERROR "Lexer source file not found: ${LEXER_FILE}")
endif()

# Read the file content
file(READ "${LEXER_FILE}" LEXER_CONTENT)

# Check if fix is needed by looking for the old pattern
string(FIND "${LEXER_CONTENT}" "int yyFlexLexer::LexerInput( char* buf, int" NEEDS_FIX_INPUT)
string(FIND "${LEXER_CONTENT}" "void yyFlexLexer::LexerOutput( const char* buf, int size )" NEEDS_FIX_OUTPUT)

# Only proceed if fixes are needed
if(NEEDS_FIX_INPUT GREATER -1 OR NEEDS_FIX_OUTPUT GREATER -1)
    set(fixes_applied 0)

    # Replace int with size_t in LexerInput return type and parameter
    string(REPLACE
        "int yyFlexLexer::LexerInput( char* buf, int"
        "size_t yyFlexLexer::LexerInput( char* buf, size_t"
        LEXER_CONTENT "${LEXER_CONTENT}")

    if(NOT "${LEXER_CONTENT}" STREQUAL "")
        math(EXPR fixes_applied "${fixes_applied} + 1")
    endif()

    # Replace int with size_t in LexerOutput parameter
    string(REPLACE
        "void yyFlexLexer::LexerOutput( const char* buf, int size )"
        "void yyFlexLexer::LexerOutput( const char* buf, size_t size )"
        LEXER_CONTENT "${LEXER_CONTENT}")

    if(NOT "${LEXER_CONTENT}" STREQUAL "")
        math(EXPR fixes_applied "${fixes_applied} + 1")
    endif()

    # Verify the fixes were applied successfully
    string(FIND "${LEXER_CONTENT}" "size_t yyFlexLexer::LexerInput" VERIFY_INPUT)
    string(FIND "${LEXER_CONTENT}" "size_t size )" VERIFY_OUTPUT)

    if(VERIFY_INPUT EQUAL -1 AND NEEDS_FIX_INPUT GREATER -1)
        message(WARNING "LexerInput type fix may have failed - expected pattern not found")
    endif()
    if(VERIFY_OUTPUT EQUAL -1 AND NEEDS_FIX_OUTPUT GREATER -1)
        message(WARNING "LexerOutput type fix may have failed - expected pattern not found")
    endif()

    # Write the modified content back
    file(WRITE "${LEXER_FILE}" "${LEXER_CONTENT}")

    # Verify write operation succeeded
    if(NOT EXISTS "${LEXER_FILE}")
        message(FATAL_ERROR "Failed to write fixed lexer file: ${LEXER_FILE}")
    endif()

    message(STATUS "Fixed lexer types for macOS ARM64 compatibility (${fixes_applied} replacements applied)")
else()
    message(STATUS "Lexer types already correct, no fix needed")
endif()
